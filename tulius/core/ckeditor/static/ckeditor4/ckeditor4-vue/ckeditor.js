/**
 * @license Copyright (c) 2003-2020, CKSource - Frederico Knabben. All rights reserved.
 * For licensing, see LICENSE.md.
 */

/* global CKEDITOR */


export default {
	name: 'ckeditor',

	render( createElement ) {
		return createElement( 'div', {}, [
			createElement( this.tagName )
		] );
	},

	props: {
		value: {
			type: String,
			default: ''
		},
		type: {
			type: String,
			default: 'classic',
			validator: type => [ 'classic', 'inline' ].includes( type )
		},
		editorUrl: {
			type: String,
			default: 'https://cdn.ckeditor.com/4.14.0/standard-all/ckeditor.js'
		},
		config: {
			type: Object,
			default: () => {}
		},
		tagName: {
			type: String,
			default: 'textarea'
		},
		readOnly: {
			type: Boolean,
			default: null // Use null as the default value, so `config.readOnly` can take precedence.
		}
	},
	mounted() {
			if ( this.$_destroyed ) {
				return;
			}
            this.build_editor();
	},

	beforeDestroy() {
		if ( this.instance ) {
			this.instance.destroy();
		}

		this.$_destroyed = true;
	},

	watch: {
		value( val ) {
			if ( this.instance.getData() !== val ) {
				this.instance.destroy();
				this.build_editor();
				//this.instance.setData( val );
			}
		},

		readOnly( val ) {
			this.instance.setReadOnly( val );
		}
	},

	methods: {
	 build_editor() {
			const config = this.config || {};

			if ( this.readOnly !== null ) {
				config.readOnly = this.readOnly;
			}

			const method = this.type === 'inline' ? 'inline' : 'replace';
			const element = this.$el.firstElementChild;
			const editor = this.instance = CKEDITOR[ method ]( element, config );

			editor.on( 'instanceReady', () => {
				const data = this.value;

				editor.fire( 'lockSnapshot' );

				editor.setData( data, { callback: () => {
					this.$_setUpEditorEvents();

					const newData = editor.getData();

					// Locking the snapshot prevents the 'change' event.
					// Trigger it manually to update the bound data.
					if ( data !== newData ) {
						this.$once( 'input', () => {
							this.$emit( 'ready', editor );
						} );

						this.$emit( 'input', newData );
					} else {
						this.$emit( 'ready', editor );
					}

					editor.fire( 'unlockSnapshot' );
				} } );
			} );

        },
		$_setUpEditorEvents() {
			const editor = this.instance;

			editor.on( 'change', evt => {
				const data = editor.getData();

				// Editor#change event might be fired without an actual data change.
				if ( this.value !== data ) {
					// The compatibility with the v-model and general Vue.js concept of input–like components.
					this.$emit( 'input', data, evt, editor );
				}
			} );

			editor.on( 'focus', evt => {
				this.$emit( 'focus', evt, editor );
			} );

			editor.on( 'blur', evt => {
				this.$emit( 'blur', evt, editor );
			} );
		}
	}
};