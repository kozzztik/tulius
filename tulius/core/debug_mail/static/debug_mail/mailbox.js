import APILoadMixin from '../app/components/api_load_mixin.js'


export default LazyComponent('debug_mail_box', {
    template: '/static/debug_mail/mailbox.html',
    mixins: [APILoadMixin,],
    data: () => ({
        mailbox: [],
        search_text: '',
        email: '',
    }),
    methods: {
        load_api(route) {
            this.email = route.params.email;
            return axios.get('/api/debug_mail/' + route.params.email + '/'
            ).then(response => {
                this.breadcrumbs = [{
                    title: "Исходящая почта",
                    url: {name: 'debug_mail_users',},
                }, {
                    title: route.params.email,
                    url: {
                        name: 'debug_mail_box',
                        params: {email: route.params.email}
                    },
                },];

                this.mailbox = response.data.result;
            })
        },
    },
})
