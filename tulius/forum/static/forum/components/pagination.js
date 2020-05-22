export default LazyComponent('pagination', {
    template: '/static/forum/components/pagination.html',
    props: ['pagination'],
    methods: {
        set_page(pk) {
            if ((pk < 1)||(pk == this.pagination.page_num)||(pk > this.pagination.pages_count)) {
                return true;
            }
            this.$router.push({path: this.$router.path, query: {page: pk}})
            return true;
        },
        page_class(page) {
            if (page == this.pagination.page_num) {
                return 'active'
            } else if ((!page)||(page < 1)||(page > this.pagination.pages_count)) {
                return 'disabled'
            } else
            return '';
        }
    }

})
