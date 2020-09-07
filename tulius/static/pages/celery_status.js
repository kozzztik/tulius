import APILoadMixin from '../app/components/api_load_mixin.js'


export default LazyComponent('celery_status', {
    template: '/static/pages/celery_status.html',
    mixins: [APILoadMixin,],
    data: () => ({
        workers: {},
    }),
    methods: {
        load_api(route) {
            return axios.get('/api/celery_status/'
            ).then(response => {
                this.breadcrumbs = [{
                    title: "Очереди",
                    url: '',
                }];
                this.workers = response.data.stats;
                for (var key in response.data.active)
                    if (response.data.active.hasOwnProperty(key))
                        this.workers[key].active = response.data.active[key];
            })
        },
    },
})
