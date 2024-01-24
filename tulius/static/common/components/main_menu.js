export default LazyComponent('main_menu', {
    template: '/static/common/components/main_menu.html',
    props: ['user'],
    data: function () {
        return {
            articles: [],
            show: '',
            sse: null,
        }
    },
    methods: {
        toggle(val) {
            this.show = (this.show == val) ? '': val;
        },
        star_to_img(star) {
            if (star == 'b') {
                return 'star_big.png'
            } else if (star == 's') {
                return 'star_win.gif'
            } else if (star == 'e') {
                return 'star.gif'
            }
        },
        scroll_down() {
            window.scrollTo({left: 0, top: document.body.scrollHeight, behavior: 'smooth'});},
        scroll_up() {window.scrollTo({left: 0, top: 0, behavior: 'smooth'});},
    },
    mounted() {
        axios.get('/api/flatpages/').then(response => {
            this.articles = response.data.pages;
        }).catch(error => this.$parent.add_message(error, "error"))
        .then(() => {});
        this.sse = new EventSource('/api/sse/');
        this.sse.addEventListener("pm", (event) => {
            const content = JSON.parse(event.data);
            if (content['.action'] == 'new_pm')
                this.$root.user.not_readed_messages = true;
        });
    }
})
