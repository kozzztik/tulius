import {LazyComponent} from '../js/vue-common.js'


export default LazyComponent('breadcrumbs', {
    template: '/static/common/components/breadcrumbs.html',
    props: ['upper', 'items'],
    mounted() {
    }
})
