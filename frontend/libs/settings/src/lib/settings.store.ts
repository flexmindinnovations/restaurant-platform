import { inject } from '@angular/core';
import { signalStore, withState, withMethods, patchState } from '@ngrx/signals';
import { rxMethod } from '@ngrx/signals/rxjs-interop';
import { tapResponse } from '@ngrx/operators';
import { pipe, switchMap } from 'rxjs';
import { PlatformSettings } from './settings.model';
import { SettingsService } from './settings.service';

export interface SettingsState {
  settings: PlatformSettings | null;
  loading: boolean;
  saving: boolean;
  successMessage: string | null;
  error: string | null;
}

const initialState: SettingsState = {
  settings: null,
  loading: false,
  saving: false,
  successMessage: null,
  error: null,
};

export const SettingsStore = signalStore(
  { providedIn: 'root' },
  withState(initialState),
  withMethods((store, service = inject(SettingsService)) => ({
    loadSettings: rxMethod<void>(
      pipe(
        switchMap(() => {
          patchState(store, { loading: true, error: null });
          return service.getSettings().pipe(
            tapResponse({
              next: (settings) => patchState(store, { settings, loading: false }),
              error: (err: unknown) => patchState(store, { error: String(err), loading: false }),
            }),
          );
        }),
      ),
    ),

    saveSettings: rxMethod<PlatformSettings>(
      pipe(
        switchMap((settings) => {
          patchState(store, { saving: true, error: null, successMessage: null });
          return service.saveSettings(settings).pipe(
            tapResponse({
              next: (updated) =>
                patchState(store, {
                  settings: updated,
                  saving: false,
                  successMessage: 'Configuration saved successfully!',
                }),
              error: (err: unknown) => patchState(store, { error: String(err), saving: false }),
            }),
          );
        }),
      ),
    ),

    clearMessages(): void {
      patchState(store, { successMessage: null, error: null });
    },
  })),
);

export type SettingsStoreType = InstanceType<typeof SettingsStore>;
