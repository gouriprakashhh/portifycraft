// editor.js (with module type)
export class ContentEditor {
    constructor() {
        this.activeElement = null;
        this.editingImage = false;
        this.initEditor();
    }

    initEditor() {
        const editorHTML = `
            <div id="editor-sidebar">
                <div id="editor-header">
                    <span>Edit</span>
                    <button id="close-btn">&times;</button>
                </div>
                <textarea id="tiny-editor"></textarea>
                <div class="p-4 border-t text-right">
                    <button id="save-btn">Save</button>
                </div>
            </div>
        `;
        document.body.insertAdjacentHTML('beforeend', editorHTML);
        this.setupEventListeners();
    }

    setupEventListeners() {
        document.querySelectorAll('.editable, .editable-image, .editable-image img').forEach(el => {
            el.addEventListener('click', (e) => this.handleElementClick(e, el));
        });

        document.getElementById('save-btn').addEventListener('click', () => this.saveChanges());
        document.getElementById('close-btn').addEventListener('click', () => this.closeEditor());
    }

    handleElementClick(e, el) {
        this.activeElement = el.closest('.editable-image') || el;
        this.editingImage = this.activeElement.tagName.toLowerCase() === 'img' || 
                           this.activeElement.classList.contains('editable-image');

        if (this.activeElement.classList.contains('editable-image')) {
            const imgEl = this.activeElement.querySelector('img');
            if (imgEl) this.activeElement = imgEl;
        }

        tinymce.get('tiny-editor')?.destroy();
        document.getElementById('editor-sidebar').classList.add('open');

        tinymce.init({
            selector: '#tiny-editor',
            menubar: false,
            height: 300,
            plugins: this.editingImage ? 'image' : '',
            toolbar: this.editingImage
                ? 'undo redo | image | link'
                : 'undo redo | bold italic | forecolor backcolor | fontsizeselect | fontselect',
            font_formats: 'Poppins=Poppins;Inter=Inter;Arial=Arial',
            fontsize_formats: '12px 14px 16px 18px 24px 36px',
            image_title: true,
            automatic_uploads: true,
            file_picker_types: 'image',
            file_picker_callback: (callback, value, meta) => {
                if (meta.filetype === 'image') {
                    const input = document.createElement('input');
                    input.setAttribute('type', 'file');
                    input.setAttribute('accept', 'image/*');
                    input.onchange = () => {
                        const file = input.files[0];
                        this.handleImageUpload(file, callback);
                    };
                    input.click();
                }
            },
            setup: (editor) => {
                editor.on('init', () => {
                    editor.setContent(
                        this.editingImage
                            ? `<img src="${this.activeElement.src}" />`
                            : this.activeElement.innerHTML
                    );
                });
            }
        });
    }

    async handleImageUpload(file, callback) {
        const formData = new FormData();
        formData.append('image', file);

        try {
            const response = await fetch('/upload-image/', {
                method: 'POST',
                body: formData
            });
            const data = await response.json();
            if (data.url) {
                callback(data.url);
            } else {
                alert('Image upload failed: No URL returned.');
            }
        } catch (error) {
            alert('Image upload failed.');
        }
    }

    saveChanges() {
        if (this.activeElement && tinymce.get('tiny-editor')) {
            const content = tinymce.get('tiny-editor').getContent();
            if (this.editingImage) {
                const match = content.match(/<img[^>]*src=["']([^"']+)["']/);
                if (match && match[1]) {
                    this.activeElement.src = match[1];
                }
            } else {
                this.activeElement.innerHTML = content;
            }
            this.closeEditor();
        }
    }

    closeEditor() {
        document.getElementById('editor-sidebar').classList.remove('open');
        tinymce.get('tiny-editor')?.destroy();
    }
}

// Initialize the editor
document.addEventListener('DOMContentLoaded', () => {
    new ContentEditor();
});
