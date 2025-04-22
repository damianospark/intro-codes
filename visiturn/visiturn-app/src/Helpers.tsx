export const overlays: any[] = [];
export function closeOverlay(overlay_index: number) {
    overlays[overlay_index].setMap(null);
}
