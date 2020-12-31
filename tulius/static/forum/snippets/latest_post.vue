<template>
    <div v-if="comment">
        <router-link :to="urls.comment(comment)">
            <span v-html="comment.user.title"></span>
        </router-link>
        <br>
        {{ forum_datetime(comment.create_time) }}
    </div>
</template>

<script>
    import Vue from 'vue'
    import {forum_datetime} from '../../common/js/vue-common.js'


    export default Vue.component('forum_latest_post', {
        props: ['comment'],
        computed: {
            urls() {return this.$parent.urls},
        },
        methods: {
            forum_datetime: (v) => forum_datetime(new Date(v)),
        },
    })
</script>