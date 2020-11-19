<template>
    <forum_reply_form :thread="thread" :comment="comment" ref="reply_form" :reply_str="reply_str">
        <template v-slot:before_form="slotProps">
            <game_forum_role_selector :variation="variation" :thread="thread" :form="slotProps.form" :editor="false"></game_forum_role_selector>
            <game_forum_role_selector :variation="variation" :thread="thread" :form="slotProps.form" :editor="true" v-if="editor"></game_forum_role_selector>
        </template>
        <template v-slot:comment="slotProps">
            <forum_comment :thread="thread" :comment="slotProps.preview_comment" :preview="true">
                <template v-slot:avatar="slotProps2">
                    <game_forum_comment_avatar
                            :variation="variation" :thread="thread"
                            :role="slotProps.preview_comment.user" :actions="$parent.$refs.thread_actions">
                    </game_forum_comment_avatar>
                </template>
            </forum_comment>
        </template>
        <template v-slot:extra_media="slotProps">
            <media_illustrations :comment="slotProps.form" editor :variation="variation">
            </media_illustrations>
        </template>
    </forum_reply_form>
</template>

<script src="./reply_form.js"></script>