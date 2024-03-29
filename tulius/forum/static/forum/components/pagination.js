export default LazyComponent('pagination', {
    template: '/static/forum/components/pagination.html',
    props: ['pagination', 'page_num'],
    methods: {
        set_page(pk) {
            if ((pk < 1)||(pk == this.page_num)||(pk > this.pagination.pages_count)) {
                return true;
            }
            var query = JSON.parse(JSON.stringify(this.$route.query));
            query['page'] = pk;
            this.$router.push({path: this.$router.path, query: query})
            return true;
        },
        page_class(page) {
            if (page == this.page_num) {
                return 'active'
            } else if ((!page)||(page < 1)||(page > this.pagination.pages_count)) {
                return 'disabled'
            } else
            return '';
        }
    }

})
