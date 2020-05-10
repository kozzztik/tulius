export default LazyComponent('user_avatar', {
    template: '/static/forum/snippets/avatar.html',
    props: ['user', 'comment'],
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
})
