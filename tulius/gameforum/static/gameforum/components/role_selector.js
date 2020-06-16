export default LazyComponent('game_forum_role_selector', {
    template: '/static/gameforum/components/role_selector.html',
    props: ['variation', 'thread', 'form'],
    methods: {
		role_name_by_id(pk) {
		    if (!pk) return 'Ведущий';
		    for (var role of this.variation.roles)
                if (role.id == pk)
                    return role.title;
            return '???';
		},
    },
    created() {
        if (this.thread.rights.user_write_roles.length > 0)
            this.form.role_id = this.thread.rights.user_write_roles[0];
    },
})
