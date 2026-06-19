import {
  ChangeDetectionStrategy,
  Component,
  inject,
  OnInit,
  input,
} from '@angular/core';
import { RouterLink } from '@angular/router';
import { MatAccordion, MatExpansionModule } from '@angular/material/expansion';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatChipsModule } from '@angular/material/chips';
import { MatCardModule } from '@angular/material/card';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatDialogModule, MatDialog } from '@angular/material/dialog';
import { MatTooltipModule } from '@angular/material/tooltip';
import { PageHeader } from '../../../shared/src/lib/page-header';
import { StatusBadge } from '../../../shared/src/lib/status-badge';
import { EmptyState } from '../../../shared/src/lib/empty-state';
import { Menu, Category } from '@app/api-client';
import { MenusStore } from './menus.store';
import { MenuItemDialog, MenuItemDialogData, MenuItemDialogResult } from './menu-item-dialog';

@Component({
  selector: 'app-menus-page',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [
    RouterLink,
    MatAccordion,
    MatExpansionModule,
    MatButtonModule,
    MatIconModule,
    MatChipsModule,
    MatCardModule,
    MatProgressBarModule,
    MatDialogModule,
    MatTooltipModule,
    PageHeader,
    StatusBadge,
    EmptyState,
  ],
  template: `
    <app-page-header title="Menus" [subtitle]="'Restaurant menus — ' + store.menus().length + ' total'">
      <a mat-stroked-button [routerLink]="['../']">
        <mat-icon>arrow_back</mat-icon> Back to restaurant
      </a>
      <button mat-flat-button color="primary" (click)="onCreateMenu()" id="create-menu-btn">
        <mat-icon>add</mat-icon> New Menu
      </button>
    </app-page-header>

    @if (store.loading()) {
      <mat-progress-bar mode="indeterminate" />
    }

    @if (!store.loading() && store.menus().length === 0) {
      <app-empty-state icon="restaurant_menu" title="No menus yet"
        message="Create your first menu to start adding categories and items.">
        <button mat-flat-button color="primary" (click)="onCreateMenu()" style="margin-top:16px">
          Create menu
        </button>
      </app-empty-state>
    }

    <mat-accordion multi class="menus-accordion">
      @for (menu of store.menus(); track menu.id) {
        <mat-expansion-panel class="menu-panel">
          <mat-expansion-panel-header>
            <mat-panel-title class="panel-title">
              <mat-icon class="menu-icon">restaurant_menu</mat-icon>
              {{ menu.name }}
            </mat-panel-title>
            <mat-panel-description class="panel-desc">
              {{ menu.categories.length }} categories
              <app-status-badge [status]="menu.is_published ? 'ACTIVE' : 'INACTIVE'" />
              <button mat-icon-button color="warn" (click)="onDeleteMenu(menu, $event)"
                matTooltip="Delete menu" aria-label="Delete menu">
                <mat-icon>delete</mat-icon>
              </button>
              <button mat-icon-button (click)="onTogglePublish(menu, $event)"
                [matTooltip]="menu.is_published ? 'Unpublish' : 'Publish'">
                <mat-icon>{{ menu.is_published ? 'unpublished' : 'publish' }}</mat-icon>
              </button>
            </mat-panel-description>
          </mat-expansion-panel-header>

          <!-- Categories -->
          @for (cat of menu.categories; track cat.id) {
            <div class="category-block">
              <div class="category-header">
                <h4 class="category-name">
                  <mat-icon class="cat-icon">category</mat-icon>
                  {{ cat.name }}
                </h4>
                <div class="category-actions">
                  <button mat-stroked-button (click)="onAddItem(menu, cat)" id="add-item-btn">
                    <mat-icon>add</mat-icon> Add item
                  </button>
                  <button mat-icon-button color="warn" (click)="onDeleteCategory(menu.id, cat.id)"
                    matTooltip="Delete category">
                    <mat-icon>delete</mat-icon>
                  </button>
                </div>
              </div>

              <!-- Items table -->
              @if (cat.items.length > 0) {
                <div class="items-table">
                  @for (item of cat.items; track item.id) {
                    <div class="item-row">
                      <span class="item-name">{{ item.name }}</span>
                      <span class="item-desc">{{ item.description }}</span>
                      <span class="item-price">{{ item.price_currency }} {{ item.price_amount }}</span>
                      <app-status-badge [status]="item.is_available ? 'ACTIVE' : 'INACTIVE'" />
                      <button mat-icon-button color="warn"
                        (click)="onDeleteItem(menu.id, item.id, cat.id)"
                        matTooltip="Remove item">
                        <mat-icon>delete</mat-icon>
                      </button>
                    </div>
                  }
                </div>
              } @else {
                <p class="no-items">No items yet. <button mat-button (click)="onAddItem(menu, cat)">Add first item</button></p>
              }
            </div>
          }

          <!-- Add category -->
          <div class="add-category-row">
            <button mat-stroked-button (click)="onAddCategory(menu.id)" id="add-category-btn">
              <mat-icon>add</mat-icon> Add category
            </button>
          </div>
        </mat-expansion-panel>
      }
    </mat-accordion>
  `,
  styles: `
    .menus-accordion { margin-top: 16px; }
    .menu-panel { margin-bottom: 8px; border-radius: 8px !important; }
    .panel-title { display: flex; align-items: center; gap: 8px; font-weight: 500; }
    .menu-icon { font-size: 20px; width: 20px; height: 20px; opacity: 0.7; }
    .panel-desc { display: flex; align-items: center; gap: 8px; justify-content: flex-end; flex: 1; }
    .category-block { padding: 8px 0 8px; border-top: 1px solid var(--mat-sys-outline-variant, #eee); }
    .category-header { display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 8px; }
    .category-name { margin: 0; display: flex; align-items: center; gap: 6px; font-size: 0.95rem; font-weight: 500; }
    .cat-icon { font-size: 18px; width: 18px; height: 18px; opacity: 0.6; }
    .category-actions { display: flex; align-items: center; gap: 4px; }
    .items-table { display: flex; flex-direction: column; gap: 4px; margin: 8px 0 8px 24px; }
    .item-row {
      display: grid;
      grid-template-columns: 1fr 2fr 100px 80px 40px;
      align-items: center;
      gap: 12px;
      padding: 6px 8px;
      border-radius: 4px;
      background: var(--mat-sys-surface-variant, #f8f8f8);
    }
    .item-name { font-weight: 500; }
    .item-desc { color: var(--mat-sys-on-surface-variant, #777); font-size: 0.85rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .item-price { font-weight: 600; color: var(--mat-sys-primary, #e65100); }
    .no-items { color: var(--mat-sys-on-surface-variant, #999); font-size: 0.85rem; margin: 8px 0 8px 24px; }
    .add-category-row { padding-top: 12px; border-top: 1px dashed var(--mat-sys-outline-variant, #ddd); margin-top: 8px; }
  `,
})
export class MenusPage implements OnInit {
  readonly restaurantId = input.required<string>();

  protected readonly store = inject(MenusStore);
  private readonly dialog = inject(MatDialog);

  ngOnInit(): void {
    this.store.loadMenus(this.restaurantId());
  }

  onCreateMenu(): void {
    const name = window.prompt('New menu name:');
    if (name?.trim()) {
      this.store.createMenu({ name: name.trim() });
    }
  }

  onDeleteMenu(menu: Menu, event: Event): void {
    event.stopPropagation();
    if (window.confirm(`Delete menu "${menu.name}"? This cannot be undone.`)) {
      this.store.deleteMenu(menu.id);
    }
  }

  onTogglePublish(menu: Menu, event: Event): void {
    event.stopPropagation();
    if (menu.is_published) {
      this.store.unpublishMenu(menu.id);
    } else {
      this.store.publishMenu(menu.id);
    }
  }

  onAddCategory(menuId: string): void {
    const name = window.prompt('Category name:');
    if (name?.trim()) {
      this.store.addCategory({ menuId, body: { name: name.trim() } });
    }
  }

  onDeleteCategory(menuId: string, categoryId: string): void {
    if (window.confirm('Delete this category and all its items?')) {
      this.store.deleteCategory({ menuId, categoryId });
    }
  }

  onAddItem(menu: Menu, cat: Category): void {
    const data: MenuItemDialogData = {
      menuId: menu.id,
      categoryId: cat.id,
      categoryName: cat.name,
    };

    const ref = this.dialog.open(MenuItemDialog, { data, width: '480px' });
    ref.afterClosed().subscribe((result: MenuItemDialogResult | undefined) => {
      if (result) {
        this.store.addItem({
          menuId: menu.id,
          categoryId: cat.id,
          body: {
            name:           result.name,
            description:    result.description ?? undefined,
            price_amount:   result.price_amount,
            price_currency: result.price_currency,
            category_id:    result.category_id,
          },
        });
      }
    });
  }

  onDeleteItem(menuId: string, itemId: string, categoryId: string): void {
    if (window.confirm('Remove this item from the menu?')) {
      this.store.deleteItem({ menuId, itemId, categoryId });
    }
  }
}
