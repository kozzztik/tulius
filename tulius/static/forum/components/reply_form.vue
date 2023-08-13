<template>
    <div ref="reply_form_parking">
        <div ref="reply_form" v-if="show_form" id="reply_form" :class="comment ? 'reply_form_max' : ''">
            <slot v-bind:preview_comment="preview_comment" name="comment" v-if="show_preview" >
                <forum_comment :thread="thread" :comment="preview_comment" :preview="true"></forum_comment>
            </slot>
            <div class="content container">
                <slot v-bind:form="form" name="before_form">
                </slot>
                <slot v-bind:form="form" name="form">
                    <div class="row form_title" style="margin-top: 0.5em; display: none" >
                        <label class="col-2 col-form-label">Название:</label>
                        <div class="col-10">
                            <input v-model="form.title" class="form-control">
                        </div>
                    </div>
                    <div class="row" style="margin-top: 0.5em;" >
                        <div class="col">
                            <tulius_ckeditor v-model="form.body" reply_form></tulius_ckeditor>
                        </div>
                    </div>
                </slot>
                <div class="row" ref="media">
                    <div class="col">
                        <forum_voting :comment="form" editor ref="voting"></forum_voting>
                    </div>
                </div>
                <forum_images :comment="form" editor ref="images"></forum_images>
                <forum_youtube_media :comment="form" editor></forum_youtube_media>
                <forum_html_media :comment="form" editor></forum_html_media>
                <slot v-bind:form="form" name="extra_media"></slot>
                <div class="row" style="margin-top: 0.5em;" >
                    <div class="col">
                        <b-dropdown v-if="!loading && (media_actions.length > 0)">
                            <template v-slot:button-content>
                                <svg class="bi bi-paperclip" width="1em" height="1em" viewBox="0 0 16 16" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
                                  <path fill-rule="evenodd" d="M4.5 3a2.5 2.5 0 0 1 5 0v9a1.5 1.5 0 0 1-3 0V5a.5.5 0 0 1 1 0v7a.5.5 0 0 0 1 0V3a1.5 1.5 0 1 0-3 0v9a2.5 2.5 0 0 0 5 0V5a.5.5 0 0 1 1 0v7a3.5 3.5 0 1 1-7 0V3z"/>
                                </svg>
                            </template>
                            <b-dropdown-item href="javascript:void(0)" v-for="(action, num) in media_actions"
                                             :key="num" :disabled="action.disabled" @click="action.action()">
                                {{action.label}}
                            </b-dropdown-item>
                        </b-dropdown>
                        <div class="float-right">
                            <a id="post-preview-link" style="margin-right: 0.5em;" v-on:click="do_preview()"
                               v-if="!loading" href="javascript:void(0)">
                                Предварительный просмотр
                            </a>
                            <a class="btn btn-primary" v-on:click="do_reply" v-if="!loading"
                               href="javascript:void(0)" :class="(form.body == '') ? 'disabled': ''">
                                <span v-if="!comment">Ответить</span>
                                <span v-if="comment">Сохранить</span>
                            </a>
                        </div>
                        <div class="progress" style="height: 24px;margin-bottom: 0px;" v-if="loading">
                            <div class="progress-bar progress-bar-striped progress-bar-animated" style="width: 100%;"></div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script src="./reply_form.js"></script>