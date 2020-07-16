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
        if (!(this.thread.rights.user_write_roles.length > 0))
            return
        var val = this.thread.rights.user_write_roles[0]

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
