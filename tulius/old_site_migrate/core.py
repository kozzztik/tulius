from django.db import transaction
from .models import *
from tulius.stories.models import Story, Variation
from tulius.games.models import GAME_STATUS_COMPLETED
from .supercore import *
from .game import migrate_game
 
def migrate_news():
    csv_file = open_file('news/news.db')
    with transaction.commit_on_success():
        for row in csv_file:
            obj = get_obj(row, OldNews)
            obj.create_time = parse_date(row[1])
            obj.title = parse_str(row[3])
            obj.body = parse_str(row[4])
            obj.save()
        objs = OldNews.objects.all()
        for obj in objs:
            old_obj = obj.news_item
            if not old_obj:
                old_obj = NewsItem()
            old_obj.caption = obj.title
            old_obj.announcement = obj.body
            old_obj.full_text = obj.body
            old_obj.is_published = True
            old_obj.published_at = obj.create_time
            old_obj.created_at = obj.create_time
            old_obj.save()
            obj.news_item = old_obj
            obj.save()
            
def migrate_users():
    csv_file = open_file('forum/users.db')
    with transaction.commit_on_success():
        for row in csv_file:
            obj = get_obj(row, OldUser)
            obj.username = parse_str_def(row, 1)
            obj.password = parse_str_def(row, 2)
            obj.email = parse_str_def(row, 3)
            obj.icq = parse_str_def(row, 4)
            obj.aol = parse_str_def(row, 5)
            obj.msn = parse_str_def(row, 6)
            obj.yahoo = parse_str_def(row, 7)
            obj.website = parse_str_def(row, 8)
            obj.city = parse_str_def(row, 9)
            obj.profession = parse_str_def(row, 10)
            obj.hobby = parse_str_def(row, 11)
            obj.subpost = parse_str_def(row, 12)
            obj.show_email = parse_str_def(row, 13) == '1'
            obj.hide_on_forum = parse_str_def(row, 14) == '1'
            obj.show_subpost = parse_str_def(row, 15) == '1'
            obj.html = parse_str_def(row, 16) == '1'
            obj.smiles = parse_str_def(row, 17) == '1'
            obj.last_visited = int(parse_str_def(row, 18, 0))
            obj.ip = parse_str_def(row, 19)
            obj.convert_smiles = parse_str_def(row, 20) == '1'
            obj.notify_by_email = parse_str_def(row, 21) == '1'
            obj.hide_trust = parse_str_def(row, 22) == '1'
            obj.rank = parse_str_def(row, 23)
            obj.save()
        objs = OldUser.objects.all()
        for obj in objs:
            old_obj = obj.user
            if not old_obj:
                old_obj = User.objects.filter(username=obj.username[:30])
                if old_obj:
                    old_obj = old_obj[0]
                else:
                    old_obj = User(username = obj.username[:30])
            old_obj.email = obj.email
            old_obj.set_password(obj.password)
            old_obj.save()
            old_obj.profile.rank = obj.rank
            old_obj.profile.show_online_status = obj.hide_on_forum
            old_obj.profile.save()
            old_obj.save()
            obj.user = old_obj
            obj.save()

def migrate_games():
    csv_file = open_file('games/index.db')
    for row in csv_file:
        obj = get_obj(row, OldGame)
        obj.title = parse_str(row[1])
        obj.comment = parse_str_def(row, 2)
        obj.status = parse_str(row[3])
        obj.save()
    objs = OldGame.objects.filter(synced=False)
    for obj in objs:
        #with transaction.commit_on_success():
            if not obj.game_id:
                old_obj = Game()
            else:
                old_obj = obj.game
            old_obj.name = obj.title
            old_obj.status = GAME_STATUS_COMPLETED
            old_obj.short_comment = obj.comment
            if not old_obj.variation_id:
                variation = Variation()
                variation.name = old_obj.name
                variation.description = old_obj.short_comment
                variation.story = Story.objects.all().order_by('-id')[0]
                variation.save()
                old_obj.variation = variation
            if not old_obj.serial_number:
                old_obj.serial_number = 1
                game_numbers = Game.objects.all().order_by('-serial_number')
                if game_numbers:
                    old_obj.serial_number = game_numbers[0].serial_number + 1
            old_obj.save()
            variation = old_obj.variation
            variation.game = old_obj
            variation.save()
            obj.game = old_obj
            obj.save()
            migrate_game(obj)
            
