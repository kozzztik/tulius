from .supercore import *
from .models import OldRole, OldUser, Role, OldGameAdmin, GameAdmin, OldGameGuest, GameGuest
from .models import OldGameWinner, GameWinner, OldIllustration, Illustration
from tulius.stories.materials_views import save_illustration

def open_game_file(path, old_game):
    return open_file('games/' + old_game.old_id + '/' + path)
                
def parse_role(row, old_game, deleted):
    obj = get_obj(row, OldRole, game=old_game)
    obj.name = parse_str_def(row, 2)
    obj.comment = parse_str_def(row, 3)
    user_id = parse_str_def(row, 1)
    obj.user = None
    if user_id:
        users = OldUser.objects.filter(old_id=user_id)
        if users: 
            obj.user = users[0]
    obj.requestable = (parse_str_def(row, 4) == 'on')
    obj.show = (parse_str_def(row, 5) == 'on')
    obj.show_trust = (parse_str_def(row, 6, 'on') == 'on')
    obj.deleted = deleted
    obj.save()

def migrate_images(old_game):
    variation = old_game.game.variation
    csv_file = open_game_file('images.db', old_game)
    if csv_file:
        for row in csv_file:
            if row:
                obj = get_obj(row, OldIllustration, game=old_game)
                obj.param1 = int(parse_str_def(row, 1))
                obj.ext = parse_str_def(row, 2)
                obj.name = parse_str_def(row, 3)
                obj.top_banner = (parse_str_def(row, 4) == '1')
                obj.bottom_banner = (parse_str_def(row, 5) == '1')
                obj.param2 = int(parse_str_def(row, 6))
                obj.save()
    objs = OldIllustration.objects.filter(game=old_game)
    for obj in objs:
        filename =  obj.old_id + '.' + obj.ext
        f = simple_open_file('game_images/' + filename, binary=True)
        if not f:
            continue
        f = ContentFile(f.read())
        if obj.top_banner or obj.bottom_banner:
            if obj.top_banner:
                if old_game.game.top_banner.name <> '':
                    try:
                        old_game.game.top_banner.delete()
                    except:
                        pass
                old_game.game.top_banner.save('%s.jpg' % (old_game.game.pk,), f)
            else:
                if old_game.game.bottom_banner.name <> '':
                    try:
                        old_game.game.bottom_banner.delete()
                    except:
                        pass
                old_game.game.bottom_banner.save('%s.jpg' % (old_game.game.pk,), f)
            continue
        if not obj.illustration_id:
            old_obj = Illustration(variation=variation)
        else:
            old_obj = obj.illustration
        old_obj.name = obj.name
        old_obj.save()
        save_illustration(None, f, filename, None, variation, old_obj)
        obj.illustration = old_obj
        obj.save()
    return objs.count()
        
def migrate_roles(old_game):
    roles = {}
    csv_file = open_game_file('users.db', old_game)
    if csv_file:
        for row in csv_file:
            if row:
                parse_role(row, old_game, False)
    csv_file = open_game_file('del_users.db', old_game)
    if csv_file:
        for row in csv_file:
            if row:
                parse_role(row, old_game, True)
    objs = OldRole.objects.filter(game=old_game)
    for obj in objs:
        if not obj.role_id:
            old_obj = Role()
        else:
            old_obj = obj.role
        old_obj.variation = obj.game.game.variation
        old_obj.name = obj.name
        old_obj.description = obj.comment
        old_obj.requestable = obj.requestable
        old_obj.show_in_character_list = obj.show
        old_obj.show_in_online_character = False
        old_obj.show_trust_marks = obj.show_trust
        old_obj.deleted = obj.deleted
        if obj.user:
            old_obj.user = obj.user.user
        else:
            old_obj.user = None
        old_obj.save()
        obj.role = old_obj
        obj.save()
        roles[obj.old_id] = obj
    return roles
        
def migrate_admins(old_game):
    csv_file = open_game_file('admin.db', old_game)
    for row in csv_file:
        if row:
            obj = get_obj(row, OldGameAdmin, game=old_game)
            obj.user = OldUser.objects.get(old_id=obj.old_id)
            obj.save()
    objs = OldGameAdmin.objects.filter(game=old_game)
    for obj in objs:
        if not obj.admin:
            old_obj = GameAdmin(game=old_game.game)
        else:
            old_obj = obj.admin
        old_obj.user = obj.user.user
        old_obj.save()
        obj.admin = old_obj
        obj.save()
    return objs[0].admin.user

def migrate_guests(old_game):
    csv_file = open_game_file('guest.db', old_game)
    if not csv_file:
        return
    for row in csv_file:
        if row:
            obj = get_obj(row, OldGameGuest, game=old_game)
            users = OldUser.objects.filter(old_id=obj.old_id)
            if users:
                obj.user = users[0]
                obj.save()
    objs = OldGameGuest.objects.filter(game=old_game)
    for obj in objs:
        if not obj.guest:
            old_obj = GameGuest(game=old_game.game)
        else:
            old_obj = obj.guest
        old_obj.user = obj.user.user
        old_obj.save()
        obj.guest = old_obj
        obj.save()

def migrate_winners(old_game, roles):
    csv_file = open_game_file('winers.db', old_game)
    if not csv_file:
        return
    for row in csv_file:
        if row:
            obj = get_obj(row, OldGameWinner, game=old_game)
            if obj.old_id in roles:
                role = roles[obj.old_id]
                if role.user and role.user.user:
                    obj.user = role.user
                    obj.save()
    objs = OldGameWinner.objects.filter(game=old_game)
    for obj in objs:
        if not obj.winner:
            old_obj = GameWinner(game=old_game.game)
        else:
            old_obj = obj.winner
        old_obj.user = obj.user.user
        old_obj.save()
        obj.winner = old_obj
        obj.save()
    
def migrate_game(old_game):
    logger.error('game starting ' + unicode(old_game) + ' ' + unicode(old_game.old_id))
    if old_game.synced:
        logger.error('game already synced. No sync needs to be done.')
        return
    old_game.introduction = open_inc_file('games/' + old_game.old_id + '/about.inc')
    old_game.save()
    logger.error('migrate images...')
    images = migrate_images(old_game)
    logger.error('Done! %s images migrated.' % (images, ))
    game = old_game.game
    game.introduction = old_game.introduction
    game.save()
    roles = migrate_roles(old_game)
    migrate_guests(old_game)
    migrate_winners(old_game, roles)
    migrate_admins(old_game)
    logger.error('cache roles...')
    roles_cache = {}
    for role in roles.values():
        roles_cache[role.id] = role
    logger.error('game finished ' + unicode(old_game) + ' ' + unicode(old_game.old_id))
    old_game.synced = True
    old_game.save()
    
