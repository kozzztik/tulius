import {LazyComponent} from '../../common/js/vue-common.js'


export default LazyComponent('user_avatar', {
    template: '/static/forum/snippets/avatar.html',
    props: ['user', 'thread'],
    methods: {
        star_to_img(star) {
            if (star == 'b') {
                return 'star_big.png'
            } else if (star == 's') {
                return 'star_win.gif'
            } else if (star == 'e') {
                return 'star.gif'
            }
        }
    },
    computed: {
        online_icon_class: function() {
            if (this.thread.online_ids.indexOf(this.user.id) != -1)
                return "online-icon-here-online";
            if (this.user.online_status === true)
                return "online-icon-online";
            if (this.user.online_status === false)
                return "online-icon-offline";
            return "";
        }
    },
})
