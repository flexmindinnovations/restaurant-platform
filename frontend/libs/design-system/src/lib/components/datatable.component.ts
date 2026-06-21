import {
  Component,
  input,
  output,
  contentChildren,
  TemplateRef,
  Directive,
  ChangeDetectionStrategy,
  inject,
  computed,
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatTableModule } from '@angular/material/table';
import { MatPaginatorModule, PageEvent } from '@angular/material/paginator';
import { MatSortModule, Sort } from '@angular/material/sort';

@Directive({
  selector: '[appDatatableCell]',
  standalone: true,
})
export class DatatableCellDirective {
  columnName = input.required<string>({ alias: 'appDatatableCell' });
  public readonly templateRef = inject<TemplateRef<{ $implicit: unknown; row: unknown }>>(TemplateRef);
}

export interface DatatableColumn {
  key: string;
  label: string;
  sortable?: boolean;
}

@Component({
  selector: 'app-datatable',
  standalone: true,
  imports: [CommonModule, MatTableModule, MatPaginatorModule, MatSortModule],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './datatable.component.html',
  styleUrl: './datatable.component.scss',
})
export class DatatableComponent {
  // Signal Inputs
  dataSource = input<unknown[]>([]);
  columns = input<DatatableColumn[]>([]);
  total = input<number>(0);
  pageSize = input<number>(10);
  pageSizeOptions = input<number[]>([5, 10, 20, 50]);
  showPaginator = input<boolean>(true);
  paginatorAriaLabel = input<string>('Table pagination');
  selectedRowId = input<string | number | null | undefined>(null);
  rowIdKey = input<string>('id');
  selectedRowClass = input<string>('');
  loading = input<boolean>(false);

  // Computed data source that returns skeleton items when loading
  tableDataSource = computed(() => {
    if (this.loading()) {
      return Array(this.pageSize() || 5).fill({});
    }
    return this.dataSource();
  });


  // Signal Outputs
  pageChange = output<PageEvent>();
  sortChange = output<Sort>();
  rowClick = output<unknown>();

  // Content children as signal
  cellTemplates = contentChildren(DatatableCellDirective);

  get displayedColumns(): string[] {
    return this.columns().map((col) => col.key);
  }

  getCellTemplate(columnName: string): TemplateRef<{ $implicit: unknown; row: unknown }> | null {
    return (
      this.cellTemplates()?.find((t) => t.columnName() === columnName)?.templateRef || null
    );
  }

  getValue(row: unknown, key: string): unknown {
    if (!row) return '';
    if (key.includes('.')) {
      return key.split('.').reduce((acc: unknown, part) => {
        if (acc && typeof acc === 'object') {
          return (acc as Record<string, unknown>)[part];
        }
        return undefined;
      }, row);
    }
    return (row as Record<string, unknown>)[key];
  }

  isSelected(row: unknown): boolean {
    const selId = this.selectedRowId();
    if (selId === null || selId === undefined || !row) {
      return false;
    }
    return (row as Record<string, unknown>)[this.rowIdKey()] === selId;
  }

  getRowClasses(row: unknown): Record<string, boolean> {
    const isSel = this.isSelected(row);
    const isLoad = this.loading();
    const classes: Record<string, boolean> = {
      'table-row': !isLoad,
      'loading-row': isLoad,
      'selected-row': isSel && !isLoad,
      'table-row--selected': isSel && !isLoad,
    };
    const customClass = this.selectedRowClass();
    if (isSel && customClass && !isLoad) {
      classes[customClass] = true;
    }
    return classes;
  }

  onRowClick(row: unknown, event: Event): void {
    if (this.loading()) return;
    const target = event.target as HTMLElement;
    const isInteractive =
      target.closest('button') ||
      target.closest('a') ||
      target.closest('input') ||
      target.closest('mat-chip-option') ||
      target.closest('mat-chip') ||
      target.closest('.mat-mdc-chip') ||
      target.closest('[role="button"]') ||
      target.tagName === 'BUTTON' ||
      target.tagName === 'A' ||
      target.tagName === 'INPUT';

    if (!isInteractive) {
      this.rowClick.emit(row);
    }
  }

}
