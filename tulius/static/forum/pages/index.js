import room_list from '../snippets/room_list.js'
import APILoadMixin from '../../app/components/api_load_mixin.js'
import {LazyComponent} from '../../common/js/vue-common.js'
import axios from '../../common/js/axios.min.js';


export default LazyComponent('forum_index_page', {
    mixins: [APILoadMixin,],
    template: '/static/forum/pages/index.html',
    data: () => ({
        breadcrumbs: [],
        loading: true,
        index: {groups: []},
        search_text: '',
    }),
    computed: {
        urls() {return this.$parent.urls},
    },
    methods: {
        load_api(route) {
            return axios.get(this.urls.root_api).then(response => {
                var api_response = response.data;
                for (var group of api_response['groups'])
                    group['collapsed'] = false;
                this.index = api_response;
                if (this.user.authenticated) {
                    axios.get(this.urls.root_api + 'collapse/').then(response => {
                        for (var key in response.data)
                            for (var group of this.index.groups)
                                if (group.id == key) {
                                    group.collapsed = response.data[key];
                                    break;
                                }
                    });
                }
                this.loading = false;
            })
        },
        collapse: function (event) {
            var group_id = event.target.attributes.groupid.nodeValue;
            for (var num in this.index.groups) {
                if (this.index.groups[num].id == group_id) {
                    var value = !this.index.groups[num].collapsed;
                    this.index.groups[num].collapsed = value;
                    axios.post(
                        this.urls.root_api + 'collapse/' + group_id, {'value': value})
                    break;
                }
            }
        },
        mark_all_as_readed() {
            this.$parent.loading_start();
            axios.post(this.urls.root_api + 'read_mark/', {'comment_id': null}
            ).then(response => {}).then(() => {
                this.$parent.loading_end();
                this.load_api(null);
            });
        },
        search_submit() {
            this.$router.push(
                this.urls.search_results({
                    text: this.search_text}
                )
            );
        },
        loading_start() {this.$parent.loading_start()},
        loading_end(breadcrumbs) {this.$parent.loading_end(breadcrumbs)},
        to_comment(pk) {
            this.$parent.loading_start();
            axios.get(this.urls.comment_api(pk)).then(response => {
                this.$parent.loading_end()
                this.$router.push(this.urls.comment(response.data));
            })
        }
    },
})
