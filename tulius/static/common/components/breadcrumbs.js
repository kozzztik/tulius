export default LazyComponent('breadcrumbs', {
    template: '/static/common/components/breadcrumbs.html',
    props: ['upper', 'items'],
    mounted() {
        $(
            this.upper ? "#top-breadcrumbs": "#bottom-breadcrumbs"
        ).rcrumbs({nbFixedCrumbs: 1, nbUncollapsableCrumbs: 1});
    }
})
