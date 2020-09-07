import APILoadMixin from '../app/components/api_load_mixin.js'


export default LazyComponent('debug_mail_users', {
    template: '/static/debug_mail/users.html',
    mixins: [APILoadMixin,],
    data: () => ({
        users: [],
        search_text: '',
    }),
    methods: {
        load_api(route) {
            return axios.get('/api/debug_mail/'
            ).then(response => {
                this.breadcrumbs = [{
                    title: "Исходящая почта",
                    url: '',
                }];
                this.users = response.data.result;
            })
        },
        do_search() {
            axios.get(
                '/api/debug_mail/?q=' + this.search_text
            ).then(response => {
                this.users = response.data.result;
            })
        },
    },
})
