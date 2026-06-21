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
  LucidePencil,
  LucideArrowUp,
  LucideArrowDown,
  LucideGripVertical,
} from '@lucide/angular';
import { MatChipsModule } from '@angular/material/chips';
import { MatCardModule } from '@angular/material/card';
import { MatDialogModule, MatDialog } from '@angular/material/dialog';
import { MatTooltipModule } from '@angular/material/tooltip';
import { CdkDragDrop, DragDropModule, moveItemInArray } from '@angular/cdk/drag-drop';
import { CommonModule } from '@angular/common';
import { tap } from 'rxjs/operators';
import { patchState } from '@ngrx/signals';

import { PageHeader } from '../../../shared/src/lib/page-header';
import { HeaderService, ConfirmDialog, ConfirmDialogData } from '@app/shared';
import { StatusBadge } from '../../../shared/src/lib/status-badge';
import { EmptyState } from '../../../shared/src/lib/empty-state';
import { Menu, Category, MenuItem, MenusService } from '@app/api-client';
import { MenusStore } from './menus.store';
import { MenuItemDialog, MenuItemDialogData, MenuItemDialogResult } from './menu-item-dialog.component';
import { CreateDialog, CreateDialogData, CreateDialogResult } from './create-dialog.component';

@Component({
  selector: 'app-menus-page',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [
    CommonModule,
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
    LucidePencil,
    LucideArrowUp,
    LucideArrowDown,
    LucideGripVertical,
    MatChipsModule,
    MatCardModule,
    MatDialogModule,
    MatTooltipModule,
    DragDropModule,
    PageHeader,
    StatusBadge,
    EmptyState,
  ],
  templateUrl: './menus-page.component.html',
  styleUrl: './menus-page.component.scss',
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

  getCurrencySymbol(currency: string): string {
    const symbols: Record<string, string> = {
      'INR': '₹',
      'USD': '$',
      'EUR': '€',
      'GBP': '£',
    };
    return symbols[currency?.toUpperCase()] || currency;
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
      onSave: (result: MenuItemDialogResult) => {
        const body = {
          name: result.name,
          description: result.description ?? undefined,
          price_amount: result.price_amount,
          price_currency: result.price_currency,
          category_id: result.category_id,
          image_url: result.image_url,
          dietary_labels: result.dietary_labels,
          preparation_time_minutes: result.preparation_time_minutes,
        };
        // Call menusService directly to return the observable, updating store state on success
        return this.menusService.addItem(menu.id, body).pipe(
          tap((item: MenuItem) => {
            const updatedMenus = this.store.menus().map((m) => {
              if (m.id !== menu.id) return m;
              const categories = m.categories.map((c) =>
                c.id === cat.id ? { ...c, items: [...c.items, item] } : c,
              );
              return { ...m, categories };
            });
            patchState(this.store as any, { menus: updatedMenus });
          })
        );
      }
    };
    this.dialog.open(MenuItemDialog, { data, width: '480px' });
  }

  onEditItem(menu: Menu, cat: Category, item: MenuItem): void {
    const data: MenuItemDialogData = {
      menuId: menu.id,
      categoryId: cat.id,
      categoryName: cat.name,
      item: {
        id: item.id,
        name: item.name,
        description: item.description,
        price_amount: item.price_amount,
        price_currency: item.price_currency,
        is_available: item.is_available,
        image_url: item.image_url,
        dietary_labels: item.dietary_labels,
        preparation_time_minutes: item.preparation_time_minutes,
      },
      onSave: (result: MenuItemDialogResult) => {
        const body = {
          name: result.name,
          description: result.description ?? undefined,
          price_amount: result.price_amount,
          price_currency: result.price_currency,
          category_id: result.category_id,
          is_available: result.is_available,
          image_url: result.image_url,
          dietary_labels: result.dietary_labels,
          preparation_time_minutes: result.preparation_time_minutes,
        };
        // Call menusService directly to return the observable, updating store state on success
        return this.menusService.updateItem(menu.id, item.id, body).pipe(
          tap(() => {
            const updatedMenus = this.store.menus().map((m) => {
              if (m.id !== menu.id) return m;
              const categories = m.categories.map((c) => {
                const items = c.items.map((i) => {
                  if (i.id === item.id) {
                    return {
                      ...i,
                      ...body,
                      price_amount: body.price_amount !== undefined ? body.price_amount : i.price_amount,
                      price_currency: body.price_currency !== undefined ? body.price_currency : i.price_currency,
                      image_url: body.image_url !== undefined ? body.image_url : i.image_url,
                    };
                  }
                  return i;
                });
                return { ...c, items };
              });
              return { ...m, categories };
            });
            patchState(this.store as any, { menus: updatedMenus });
          })
        );
      }
    };
    this.dialog.open(MenuItemDialog, { data, width: '480px' });
  }

  onDeleteItem(menuId: string, itemId: string, categoryId: string): void {
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
        if (confirmed) {
          this.store.deleteItem({ menuId, itemId, categoryId });
        }
      });
  }

  onItemDrop(event: CdkDragDrop<MenuItem[]>, menuId: string, categoryId: string): void {
    const menu = this.store.menus().find((m) => m.id === menuId);
    if (!menu) return;
    const category = menu.categories.find((c) => c.id === categoryId);
    if (!category) return;

    const items = [...category.items];
    moveItemInArray(items, event.previousIndex, event.currentIndex);

    const reorderedItems = items.map((item, index) => ({
      ...item,
      display_order: index,
    }));

    this.store.updateLocalItemsOrder(menuId, categoryId, reorderedItems);

    reorderedItems.forEach((item) => {
      // Find the original item in the store to see if display_order changed
      const originalItem = category.items.find((i) => i.id === item.id);
      if (originalItem && originalItem.display_order === item.display_order) {
        return;
      }
      this.store.updateItem({
        menuId,
        itemId: item.id,
        body: {
          display_order: item.display_order,
          category_id: categoryId,
        },
      });
    });
  }

  moveItem(menuId: string, categoryId: string, item: MenuItem, direction: number): void {
    const menu = this.store.menus().find((m) => m.id === menuId);
    if (!menu) return;
    const category = menu.categories.find((c) => c.id === categoryId);
    if (!category) return;

    const items = [...category.items];
    const currentIndex = items.findIndex((i) => i.id === item.id);
    if (currentIndex === -1) return;

    const newIndex = currentIndex + direction;
    if (newIndex < 0 || newIndex >= items.length) return;

    moveItemInArray(items, currentIndex, newIndex);

    const reorderedItems = items.map((itm, index) => ({
      ...itm,
      display_order: index,
    }));

    this.store.updateLocalItemsOrder(menuId, categoryId, reorderedItems);

    reorderedItems.forEach((itm) => {
      // Find original item in the store to see if display_order changed
      const originalItem = category.items.find((i) => i.id === itm.id);
      if (originalItem && originalItem.display_order === itm.display_order) {
        return;
      }
      this.store.updateItem({
        menuId,
        itemId: itm.id,
        body: {
          display_order: itm.display_order,
          category_id: categoryId,
        },
      });
    });
  }
}
