import {
  ChangeDetectionStrategy,
  Component,
  inject,
  OnInit,
  OnDestroy,
  effect,
  input,
} from '@angular/core';
import { RouterLink } from '@angular/router';
import { MatAccordion, MatExpansionModule } from '@angular/material/expansion';
import { MatButtonModule } from '@angular/material/button';
import {
  LucideArrowLeft,
  LucidePlus,
  LucideUtensilsCrossed,
  LucideTrash2,
  LucideLayoutGrid,
  LucideEyeOff,
  LucideEye,
} from '@lucide/angular';
import { MatChipsModule } from '@angular/material/chips';
import { MatCardModule } from '@angular/material/card';

import { MatDialogModule, MatDialog } from '@angular/material/dialog';
import { MatTooltipModule } from '@angular/material/tooltip';
import { PageHeader } from '../../../shared/src/lib/page-header';
import { HeaderService, ConfirmDialog, ConfirmDialogData } from '@app/shared';
import { StatusBadge } from '../../../shared/src/lib/status-badge';
import { EmptyState } from '../../../shared/src/lib/empty-state';
import { Menu, Category, MenusService } from '@app/api-client';
import { MenusStore } from './menus.store';
import { MenuItemDialog, MenuItemDialogData, MenuItemDialogResult } from './menu-item-dialog';
import { CreateDialog, CreateDialogData, CreateDialogResult } from './create-dialog';

@Component({
  selector: 'app-menus-page',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [
    RouterLink,
    MatAccordion,
    MatExpansionModule,
    MatButtonModule,
    LucideArrowLeft,
    LucidePlus,
    LucideUtensilsCrossed,
    LucideTrash2,
    LucideLayoutGrid,
    LucideEyeOff,
    LucideEye,
    MatChipsModule,
    MatCardModule,
    MatDialogModule,
    MatTooltipModule,
    PageHeader,
    StatusBadge,
    EmptyState,
  ],
  template: `
    <app-page-header
      title="Menus"
      [subtitle]="'Restaurant menus — ' + store.menus().length + ' total'"
    >
      <a mat-stroked-button [matTooltip]="backButtonTooltip" [routerLink]="['../']">
        <svg lucideArrowLeft [size]="18"></svg> Back to restaurant
      </a>
      <button mat-flat-button  [matTooltip]="newMenuButtonTooltip" color="primary" (click)="onCreateMenu()" id="create-menu-btn">
        <svg lucidePlus [size]="18"></svg> New Menu
      </button>
    </app-page-header>

    @if (!store.loading() && store.menus().length === 0) {
      <app-empty-state
        icon="utensils-crossed"
        title="No menus yet"
        message="Create your first menu to start adding categories and items."
      >
        <button mat-flat-button color="primary" (click)="onCreateMenu()" style="margin-top:16px">
          Create menu
        </button>
      </app-empty-state>
    }

    <mat-accordion multi class="menus-accordion">
      @for (menu of store.menus(); track menu.id) {
        <mat-expansion-panel class="menu-panel" [expanded]="$first">
          <mat-expansion-panel-header>
            <mat-panel-title class="panel-title">
              <span class="menu-icon-wrap">
                <svg lucideUtensilsCrossed [size]="16" style="color: var(--color-primary)"></svg>
              </span>
              {{ menu.name }}
            </mat-panel-title>
            <mat-panel-description class="panel-desc">
              <span class="category-count">{{ menu.categories.length }} categories</span>
              <app-status-badge [status]="menu.is_active ? 'ACTIVE' : 'INACTIVE'" />
              <button
                mat-icon-button
                (click)="onToggleActive(menu, $event)"
                [matTooltip]="menu.is_active ? 'Deactivate menu' : 'Activate menu'"
                [class]="menu.is_active ? 'action-icon-btn deactivate-btn' : 'action-icon-btn activate-btn'"
              >
                @if (menu.is_active) {
                  <svg lucideEyeOff [size]="16"></svg>
                } @else {
                  <svg lucideEye [size]="16"></svg>
                }
              </button>
              <button
                mat-icon-button
                (click)="onDeleteMenu(menu, $event)"
                matTooltip="Delete menu"
                aria-label="Delete menu"
                class="action-icon-btn delete-btn"
              >
                <svg lucideTrash2 [size]="16"></svg>
              </button>
            </mat-panel-description>
          </mat-expansion-panel-header>

          <div class="panel-body">
            @for (cat of menu.categories; track cat.id) {
              <div class="category-block">
                <div class="category-header">
                  <h4 class="category-name">
                    <svg lucideLayoutGrid [size]="16" style="color: var(--color-accent)"></svg>
                    {{ cat.name }}
                  </h4>
                  <div class="category-actions">
                    <button mat-stroked-button (click)="onAddItem(menu, cat)" id="add-item-btn" class="compact-btn">
                      <svg lucidePlus [size]="16"></svg> Add item
                    </button>
                    <button
                      mat-icon-button
                      (click)="onDeleteCategory(menu.id, cat.id)"
                      matTooltip="Delete category"
                      class="action-icon-btn delete-btn"
                    >
                      <svg lucideTrash2 [size]="16" style="color: var(--color-error)"></svg>
                    </button>
                  </div>
                </div>

                @if (cat.items.length > 0) {
                  <div class="items-table">
                    @for (item of cat.items; track item.id) {
                      <div class="item-row">
                        <div class="item-info">
                          <span class="item-name">{{ item.name }}</span>
                          @if (item.description) {
                            <span class="item-desc">{{ item.description }}</span>
                          }
                        </div>
                        <div class="item-actions">
                          <span class="item-price">{{ item.price_currency }} {{ item.price_amount }}</span>
                          <app-status-badge [status]="item.is_available ? 'ACTIVE' : 'INACTIVE'" />
                          <button
                            mat-icon-button
                            (click)="onDeleteItem(menu.id, item.id, cat.id)"
                            matTooltip="Remove item"
                            class="action-icon-btn delete-btn"
                          >
                            <svg lucideTrash2 [size]="16" style="color: var(--color-error)"></svg>
                          </button>
                        </div>
                      </div>
                    }
                  </div>
                } @else {
                  <p class="no-items">
                    No items yet.
                    <button mat-button color="primary" (click)="onAddItem(menu, cat)">Add first item</button>
                  </p>
                }
              </div>
            }

            <div class="add-category-row">
              <button mat-stroked-button (click)="onAddCategory(menu.id)" id="add-category-btn" class="add-category-btn">
                <svg lucidePlus [size]="16"></svg> Add category
              </button>
            </div>
          </div>
        </mat-expansion-panel>
      }
    </mat-accordion>
  `,
  styles: `
    :host {
      display: block;
    }

    .menus-accordion {
      display: flex;
      flex-direction: column;
      gap: 12px;
      margin-top: 20px;
    }

    .menu-panel {
      border-radius: 0 !important;
      border: 1px solid var(--color-border) !important;
      background-color: var(--color-surface-1) !important;
      box-shadow: var(--shadow-sm) !important;
      transition: box-shadow 0.2s ease;
    }

    .menu-panel:hover {
      box-shadow: var(--shadow-md) !important;
    }

    .menu-panel ::ng-deep .mat-expansion-panel-header {
      background-color: var(--color-surface-1) !important;
      padding: 0 16px !important;
      height: 52px !important;
      font-size: 14px;
    }

    .menu-panel ::ng-deep .mat-expansion-panel-header:hover {
      background-color: var(--color-surface-2) !important;
    }

    .menu-panel ::ng-deep .mat-expansion-panel-body {
      padding: 0 !important;
    }

    .panel-title {
      display: flex;
      align-items: center;
      gap: 8px;
      font-weight: 600;
      font-size: 14px;
      color: var(--color-text-primary);
    }

    .menu-icon-wrap {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      width: 28px;
      height: 28px;
      border-radius: 0;
      background-color: var(--color-primary-subtle);
      flex-shrink: 0;
    }

    svg[class*='lucide'] {
      vertical-align: middle;
    }

    .panel-desc {
      display: flex;
      align-items: center;
      gap: 10px;
      justify-content: flex-end;
      flex: 1;
    }

    .category-count {
      font-size: 13px;
      color: var(--color-text-tertiary);
      font-weight: 400;
    }

    .action-icon-btn {
      width: 32px !important;
      height: 32px !important;
      padding: 0 !important;
      display: inline-flex !important;
      align-items: center !important;
      justify-content: center !important;
      border-radius: 50% !important;
      transition: background-color 0.15s ease !important;
      --mat-icon-button-hover-state-layer-opacity: 0;
      --mat-icon-button-pressed-state-layer-opacity: 0;

      .mat-mdc-button-touch-target {
        width: 32px !important;
        height: 32px !important;
      }

      svg {
        width: 16px !important;
        height: 16px !important;
      }
    }

    .activate-btn {
      color: var(--color-success, #16a34a) !important;
    }

    .activate-btn:hover {
      background-color: var(--color-success-bg, #f0fdf4) !important;
    }

    .deactivate-btn {
      color: var(--color-warning, #d97706) !important;
    }

    .deactivate-btn:hover {
      background-color: var(--color-warning-bg, #fffbeb) !important;
    }

    .delete-btn {
      color: var(--color-error) !important;
    }

    .delete-btn:hover {
      background-color: var(--color-error-bg) !important;
    }

    .panel-body {
      padding: 4px 20px 20px;
    }

    .category-block {
      padding: 16px;
      margin-top: 12px;
      background-color: var(--color-surface-2);
      border-radius: 0;
      border: 1px solid var(--color-border-light);
    }

    .category-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 8px;
      margin-bottom: 4px;
    }

    .category-name {
      margin: 0;
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 14px;
      font-weight: 600;
      color: var(--color-text-primary);
    }

    .category-actions {
      display: flex;
      align-items: center;
      gap: 6px;
    }

    .compact-btn {
      font-size: 13px !important;
      height: 34px !important;
      padding: 0 14px !important;
    }

    .items-table {
      display: flex;
      flex-direction: column;
      gap: 2px;
      margin-top: 12px;
      border-radius: 0;
      overflow: hidden;
      border: 1px solid var(--color-border-light);
    }

    .item-row {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      padding: 10px 14px;
      background-color: var(--color-surface-1);
      border-bottom: 1px solid var(--color-border-light);
      transition: background-color 0.15s ease;
    }

    .item-row:last-child {
      border-bottom: none;
    }

    .item-row:hover {
      background-color: var(--color-surface-2);
    }

    .item-info {
      display: flex;
      flex-direction: column;
      min-width: 0;
      flex: 1;
    }

    .item-name {
      font-weight: 500;
      font-size: 14px;
      color: var(--color-text-primary);
    }

    .item-desc {
      color: var(--color-text-secondary);
      font-size: 13px;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    .item-actions {
      display: flex;
      align-items: center;
      gap: 8px;
      flex-shrink: 0;
    }

    .item-price {
      font-weight: 600;
      font-size: 14px;
      color: var(--color-primary);
      white-space: nowrap;
    }

    .no-items {
      color: var(--color-text-tertiary);
      font-size: 13px;
      margin: 12px 0 0;
      padding: 12px 0 0;
      display: flex;
      align-items: center;
      gap: 4px;
    }

    .add-category-row {
      padding-top: 16px;
      margin-top: 12px;
      border-top: 1px dashed var(--color-border-light);
      display: flex;
      justify-content: center;
    }

    .add-category-btn {
      border-style: dashed !important;
      color: var(--color-text-secondary) !important;
      font-size: 13px !important;
      height: 38px !important;
      padding: 0 20px !important;
      border-color: var(--color-border) !important;
      transition: all 0.15s ease !important;
    }

    .add-category-btn:hover {
      color: var(--color-primary) !important;
      border-color: var(--color-primary) !important;
      background-color: var(--color-primary-subtle) !important;
    }
  `,
})
export class MenusPage implements OnInit, OnDestroy {
  readonly id = input.required<string>();

  protected readonly store = inject(MenusStore);
  private readonly dialog = inject(MatDialog);
  private readonly headerService = inject(HeaderService);
  private readonly menusService = inject(MenusService);
  readonly backButtonTooltip = 'Back';
  readonly newMenuButtonTooltip = 'Create new menu';

  constructor() {
    effect(() => {
      this.headerService.setLoading(this.store.loading());
    });
  }

  ngOnInit(): void {
    this.store.loadMenus(this.id());
  }

  ngOnDestroy(): void {
    this.headerService.setLoading(false);
  }

  onCreateMenu(): void {
    const data: CreateDialogData = {
      title: 'Create New Menu',
      nameLabel: 'Menu Name',
      namePlaceholder: 'e.g. Dinner Menu, Lunch Specials',
    };
    const ref = this.dialog.open(CreateDialog, { data, width: '480px' });
    ref.afterClosed().subscribe((result: CreateDialogResult | undefined) => {
      if (result) {
        this.store.createMenu({
          name: result.name,
          description: result.description || undefined,
        });
      }
    });
  }

  onDeleteMenu(menu: Menu, event: Event): void {
    event.stopPropagation();
    const data: ConfirmDialogData = {
      title: 'Delete Menu',
      message: `Are you sure you want to delete "${menu.name}"? All categories and items within this menu will be permanently removed.`,
      confirmLabel: 'Delete',
      variant: 'danger',
      onConfirm: () => this.menusService.delete(menu.id),
    };
    this.dialog.open(ConfirmDialog, { data, width: '420px' })
      .afterClosed()
      .subscribe((confirmed: boolean) => {
        if (confirmed) this.store.loadMenus(this.id());
      });
  }

  onToggleActive(menu: Menu, event: Event): void {
    event.stopPropagation();
    if (menu.is_active) {
      this.store.deactivateMenu(menu.id);
    } else {
      this.store.activateMenu(menu.id);
    }
  }

  onAddCategory(menuId: string): void {
    const data: CreateDialogData = {
      title: 'Add Category',
      nameLabel: 'Category Name',
      namePlaceholder: 'e.g. Appetizers, Desserts',
    };
    const ref = this.dialog.open(CreateDialog, { data, width: '480px' });
    ref.afterClosed().subscribe((result: CreateDialogResult | undefined) => {
      if (result) {
        this.store.addCategory({
          menuId,
          body: {
            name: result.name,
            description: result.description || undefined,
          },
        });
      }
    });
  }

  onDeleteCategory(menuId: string, categoryId: string): void {
    const data: ConfirmDialogData = {
      title: 'Delete Category',
      message: 'This will permanently delete the category and all items within it.',
      confirmLabel: 'Delete',
      variant: 'danger',
      onConfirm: () => this.menusService.deleteCategory(menuId, categoryId),
    };
    this.dialog.open(ConfirmDialog, { data, width: '420px' })
      .afterClosed()
      .subscribe((confirmed: boolean) => {
        if (confirmed) this.store.loadMenus(this.id());
      });
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
            name: result.name,
            description: result.description ?? undefined,
            price_amount: result.price_amount,
            price_currency: result.price_currency,
            category_id: result.category_id,
          },
        });
      }
    });
  }

  onDeleteItem(menuId: string, itemId: string, _categoryId: string): void {
    const data: ConfirmDialogData = {
      title: 'Delete Item',
      message: 'Are you sure you want to remove this item from the menu?',
      confirmLabel: 'Delete',
      variant: 'danger',
      onConfirm: () => this.menusService.deleteItem(menuId, itemId),
    };
    this.dialog.open(ConfirmDialog, { data, width: '420px' })
      .afterClosed()
      .subscribe((confirmed: boolean) => {
        if (confirmed) this.store.loadMenus(this.id());
      });
  }
}
