<template>
    <div v-if="!loading">
        <game_forum_thread_actions :variation="variation" :thread="thread" :upper="true" ref="thread_actions"></game_forum_thread_actions>
        <forum_thread_comments :thread="thread" v-model="comments_page" v-if="!loading" ref="comments">
            <template v-slot:comment="slotProps">
                <forum_comment :thread="thread" :comment="slotProps.comment">
                    <template v-slot:avatar="slotProps">
                        <game_forum_comment_avatar
                                :variation="variation" :thread="thread"
                                :role="slotProps.comment.user" :actions="$refs.thread_actions">
                        </game_forum_comment_avatar>
                    </template>
                    <template v-slot:extra_media="slotProps">
                        <media_illustrations :comment="slotProps.comment" :variation="variation">
                        </media_illustrations>
                    </template>
                </forum_comment>
            </template>
        </forum_thread_comments>
        <forum_reply_form :thread="thread" ref="reply_form" v-if="!loading && thread.rights.write"></forum_reply_form>
        <game_forum_online_status :variation="variation" :thread="thread"></game_forum_online_status>
        <game_forum_thread_actions :variation="variation" :thread="thread" :upper="false"></game_forum_thread_actions>
    </div>
</template>

<script src="./thread.js"></script>