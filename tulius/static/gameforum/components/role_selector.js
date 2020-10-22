import {LazyComponent} from '../../common/js/vue-common.js'


export default LazyComponent('game_forum_role_selector', {
    template: '/static/gameforum/components/role_selector.html',
    props: ['variation', 'thread', 'form', 'editor'],
    methods: {
		role_name_by_id(pk) {
		    if (!pk) return '---';
		    for (var role of this.variation.roles)
                if (role.id == pk)
                    return role.title;
            return '???';
		},
    },
    created() {
        var assigned = [];
        for (var role of this.variation.roles)
            if (role.assigned) assigned.push(role.id);
        if (!(this.thread.rights.user_write_roles.length > 0))
            return
        var assigned_write = []
        for (var role_id of assigned)
            if (this.thread.rights.user_write_roles.indexOf(role_id) >= 0)
                assigned_write.push(role_id);
        var val = assigned_write.length > 0 ?
            assigned_write[0] : this.thread.rights.user_write_roles[0];
        if (!this.form.id) {
            this.form.role_id = val
        } else {
            if (this.editor)
                this.form.edit_role_id = val
            else
                this.form.role_id = this.form.user.id;
        }
    },
})
