import { ChangeDetectionStrategy, Component, EventEmitter, input, output, signal, effect } from '@angular/core';
import { CommonModule } from '@angular/common';
import { LucideUpload, LucideTrash2, provideLucideIcons } from '@lucide/angular';

@Component({
  selector: 'app-image-picker',
  standalone: true,
  imports: [CommonModule, LucideUpload, LucideTrash2],
  providers: [provideLucideIcons(LucideUpload, LucideTrash2)],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="image-picker-container">
      <div
        class="dropzone"
        [class.dragover]="isDragOver()"
        (dragover)="onDragOver($event)"
        (dragleave)="onDragLeave()"
        (drop)="onDrop($event)"
        (click)="fileInput.click()"
        (keydown.enter)="fileInput.click()"
        (keydown.space)="$event.preventDefault(); fileInput.click()"
        tabindex="0"
        role="button"
        aria-label="Upload item images"
      >
        <input
          #fileInput
          type="file"
          [multiple]="multiple()"
          accept="image/*"
          (change)="onFileSelected($event)"
          style="display: none"
        />
        <div class="dropzone-content">
          <svg lucideUpload [size]="32" class="upload-icon" aria-hidden="true"></svg>
          <p class="upload-text">
            <strong>Click to upload</strong> or drag and drop
          </p>
          <p class="upload-hint">Images only (PNG, JPG, WEBP up to {{ maxSizeMb() }}MB)</p>
        </div>
      </div>

      @if (images().length > 0) {
        <div class="previews-grid" role="list" aria-label="Selected image previews">
          @for (img of images(); track img; let idx = $index) {
            <div class="preview-card" role="listitem">
              <img [src]="img" alt="Preview of uploaded item image" class="preview-img" />
              <div class="overlay">
                <button
                  type="button"
                  class="remove-btn"
                  (click)="removeImage(idx, $event)"
                  aria-label="Remove image"
                >
                  <svg lucideTrash2 [size]="16" aria-hidden="true"></svg>
                </button>
              </div>
            </div>
          }
        </div>
      }
    </div>
  `,
  styles: `
    .image-picker-container {
      display: flex;
      flex-direction: column;
      gap: 16px;
      width: 100%;
      margin-bottom: 8px;
    }
    .dropzone {
      border: 2px dashed var(--color-border, #e0e0e0);
      border-radius: 8px;
      padding: 24px;
      text-align: center;
      cursor: pointer;
      background: var(--color-bg-offset, #fafafa);
      transition: all 0.2s ease-in-out;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;

      &:hover, &.dragover {
        border-color: var(--color-primary, #1976d2);
        background: rgba(25, 118, 210, 0.04);
      }
    }
    .dropzone-content {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 8px;
    }
    .upload-icon {
      color: var(--color-text-secondary, #757575);
      opacity: 0.7;
    }
    .upload-text {
      margin: 0;
      font-size: 0.875rem;
      color: var(--color-text-primary, #212121);
      strong {
        color: var(--color-primary, #1976d2);
      }
    }
    .upload-hint {
      margin: 0;
      font-size: 0.75rem;
      color: var(--color-text-secondary, #757575);
      opacity: 0.8;
    }
    .previews-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(80px, 1fr));
      gap: 12px;
      width: 100%;
    }
    .preview-card {
      position: relative;
      aspect-ratio: 1;
      border-radius: 6px;
      overflow: hidden;
      border: 1px solid var(--color-border, #e0e0e0);
      background: #000;
      box-shadow: 0 1px 3px rgba(0,0,0,0.1);

      &:hover .overlay {
        opacity: 1;
      }
    }
    .preview-img {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }
    .overlay {
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: rgba(0, 0, 0, 0.4);
      display: flex;
      align-items: center;
      justify-content: center;
      opacity: 0;
      transition: opacity 0.15s ease-in-out;
    }
    .remove-btn {
      background: var(--color-error, #f44336);
      color: #fff;
      border: none;
      border-radius: 50%;
      width: 28px;
      height: 28px;
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      box-shadow: 0 2px 4px rgba(0,0,0,0.2);
      transition: transform 0.1s ease;

      &:hover {
        transform: scale(1.1);
        background: #d32f2f;
      }
    }
  `,
})
export class ImagePicker {
  readonly multiple = input<boolean>(true);
  readonly maxSizeMb = input<number>(5);
  readonly initialImages = input<string[]>([]);
  readonly imagesChanged = output<string[]>();

  protected readonly images = signal<string[]>([]);
  protected readonly isDragOver = signal<boolean>(false);

  constructor() {
    effect(() => {
      this.images.set(this.initialImages() || []);
    });
  }

  onDragOver(event: DragEvent): void {
    event.preventDefault();
    this.isDragOver.set(true);
  }

  onDragLeave(): void {
    this.isDragOver.set(false);
  }

  onDrop(event: DragEvent): void {
    event.preventDefault();
    this.isDragOver.set(false);
    if (event.dataTransfer?.files) {
      this.processFiles(event.dataTransfer.files);
    }
  }

  onFileSelected(event: Event): void {
    const inputEl = event.target as HTMLInputElement;
    if (inputEl.files) {
      this.processFiles(inputEl.files);
    }
  }

  removeImage(index: number, event: Event): void {
    event.stopPropagation();
    const current = [...this.images()];
    current.splice(index, 1);
    this.images.set(current);
    this.imagesChanged.emit(current);
  }

  private processFiles(files: FileList): void {
    const validFiles: File[] = [];
    const maxBytes = this.maxSizeMb() * 1024 * 1024;

    for (let i = 0; i < files.length; i++) {
      const file = files[i];
      if (!file.type.startsWith('image/')) {
        continue;
      }
      if (file.size > maxBytes) {
        alert(`File ${file.name} exceeds the maximum size of ${this.maxSizeMb()}MB.`);
        continue;
      }
      validFiles.push(file);
    }

    if (validFiles.length === 0) return;

    const readPromises = validFiles.map((file) => {
      return new Promise<string>((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = (e) => {
          if (e.target?.result) {
            resolve(e.target.result as string);
          } else {
            reject(new Error('Failed to read file'));
          }
        };
        reader.onerror = () => reject(new Error('File reading error'));
        reader.readAsDataURL(file);
      });
    });

    Promise.all(readPromises)
      .then((base64Strings) => {
        if (this.multiple()) {
          const current = [...this.images(), ...base64Strings];
          this.images.set(current);
          this.imagesChanged.emit(current);
        } else {
          this.images.set([base64Strings[0]]);
          this.imagesChanged.emit([base64Strings[0]]);
        }
      })
      .catch((err) => {
        console.error('Error reading files:', err);
      });
  }
}
