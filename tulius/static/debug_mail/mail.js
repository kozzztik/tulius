import APILoadMixin from '../app/components/api_load_mixin.js'
import {LazyComponent} from '../common/js/vue-common.js'
import axios from '../common/js/axios.min.js';


export default LazyComponent('debug_mail_box', {
    template: '/static/debug_mail/mail.html',
    mixins: [APILoadMixin,],
    data: () => ({
        body: '',
    }),
    methods: {
        load_api(route) {
            this.email = route.params.email;
            return axios.get(
                '/api/debug_mail/' + route.params.email + '/' + route.params.pk + '/'
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
                },{
                    title: route.params.pk,
                    url: '',
                },];

                this.body = response.data.replace(/[\n]/g, '<br>');
            })
        },
    },
})
