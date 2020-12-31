/**
 * @license Copyright (c) 2003-2020, CKSource - Frederico Knabben. All rights reserved.
 * For licensing, see LICENSE.md or https://ckeditor.com/legal/ckeditor-oss-license
 */

( function() {
	CKEDITOR.plugins.add( 'replyformmax', {
		icons: 'replyformmax',
		hidpi: true,
		init: function( editor ) {
			// Maximize plugin isn't available in inline mode yet.
			if ( editor.elementMode == CKEDITOR.ELEMENT_MODE_INLINE )
				return;

			// Retain state after mode switches.
			var savedState = CKEDITOR.TRISTATE_OFF;

			editor.addCommand( 'replyformmax', {
				modes: { wysiwyg: true, source: true },
				readOnly: 1,
				editorFocus: false,
				exec: function() {
					var form_classes = document.getElementById("reply_form").classList;
					var main_classes = document.getElementById("content-center").classList;

					if ( this.state == CKEDITOR.TRISTATE_OFF ) {
						form_classes.add("reply_form_max");
						main_classes.add("reply_form_only");
					}
					else if ( this.state == CKEDITOR.TRISTATE_ON ) {
                        form_classes.remove("reply_form_max");
                        main_classes.remove("reply_form_only");
                        document.getElementById("reply_form").scrollIntoView(false);
                    }

					this.toggleState();

					// Toggle button label.
					var button = this.uiItems[ 0 ];
					// Only try to change the button if it exists (https://dev.ckeditor.com/ticket/6166)
					if ( button ) {
						var label = ( this.state == CKEDITOR.TRISTATE_OFF ) ? "Перейти к расширенной форме" : "Перейти к быстрой форме";
						var buttonNode = CKEDITOR.document.getById( button._.id );
						buttonNode.getChild( 1 ).setHtml( label );
						buttonNode.setAttribute( 'title', label );
						buttonNode.setAttribute( 'href', 'javascript:void("' + label + '");' ); // jshint ignore:line
					}
					savedState = this.state;
					editor.fire( 'maximize', this.state );
				},
				canUndo: false
			} );

			editor.ui.addButton && editor.ui.addButton( 'Replyformmax', {
				label: "Перейти к расширенной форме",
				command: 'replyformmax',
				toolbar: 'tools,10'
			} );

			// Restore the command state after mode change, unless it has been changed to disabled (https://dev.ckeditor.com/ticket/6467)
			editor.on( 'mode', function() {
				var command = editor.getCommand( 'replyformmax' );
				command.setState( command.state == CKEDITOR.TRISTATE_DISABLED ? CKEDITOR.TRISTATE_DISABLED : savedState );
			}, null, null, 100 );
		}
	} );
} )();
