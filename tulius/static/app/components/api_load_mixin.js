export default {
    data: function () {
        return {
          breadcrumbs: null,
        }
    },
    computed: {
        user() {return this.$root.user},
    },
    methods: {
        _load_api(route) {
            var res = this.load_api(route);
            if (res && (typeof res.then === 'function')) {
                this.$parent.loading_start();
                res.catch().then(() => this.$parent.loading_end(this.breadcrumbs));
            }
        },
    },
    mounted() {
        this._load_api(this.$route)
    },
    beforeRouteUpdate (to, from, next) {
        this._load_api(to);
        next();
    },
}