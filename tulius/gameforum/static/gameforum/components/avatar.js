export default LazyComponent('game_forum_comment_avatar', {
    template: '/static/gameforum/components/avatar.html',
    props: ['variation', 'thread', 'role', 'actions'],
    computed: {
        online_icon_class: function() {
            if (this.thread.online_ids.indexOf(this.role.id) != -1)
                return "online-icon-here-online";
            if (this.role.online_status === true)
                return "online-icon-online";
            if (this.role.online_status === false)
                return "online-icon-offline";
            return "online-icon-hidden";
        },
        user: function() {return this.$root.user;},
        my_trust: function() {
            var role = this.original_role(this.role.id);
		    if (role)
		        return role.my_trust || 0;
		    return 0;
		},
		trust_value: function() {
            var role = this.original_role(this.role.id);
		    if (role)
		        return role.trust_value || 0;
		    return 0;
		},
    },
    methods: {
		do_trustmark(value) {
		    axios.post(
		        this.variation.url + 'trust_mark/' + this.role.id + '/',
		        {value: value}
            ).then(response => {
                var role = this.original_role(this.role.id);
                role.my_trust = response.data.my_trust;
                role.trust_value = response.data.trust_value;
            }).catch(error => this.$root.add_message(error, "error"));
		},
		original_role(role_id) {
		    for (var role of this.variation.characters)
		        if (role.id == role_id)
		            return role
		},
    },
})
