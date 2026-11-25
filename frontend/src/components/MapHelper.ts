import L from 'leaflet';
import markerIcon2x from 'leaflet/dist/images/marker-icon-2x.png';
import markerIcon from 'leaflet/dist/images/marker-icon.png';
import markerShadow from 'leaflet/dist/images/marker-shadow.png';

// Fix Leaflet's default icon path issues in Vite/Webpack
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconUrl: markerIcon,
  iconRetinaUrl: markerIcon2x,
  shadowUrl: markerShadow,
});

export const createCustomPin = (color: 'blue' | 'green' | 'red' | 'teal' | 'amber' | 'purple' | 'cyan' | 'forest' | 'emerald') => {
  const colorMap: Record<string, string> = {
    forest: '#073B32',
    emerald: '#119B72',
    green: '#119B72',
    teal: '#0B4F43',
    blue: '#0E6254',
    amber: '#E9A23B',
    red: '#E45B55',
    purple: '#4F5D75',
    cyan: '#119B72'
  };
  const hex = colorMap[color] || '#119B72';

  return L.divIcon({
    className: 'custom-map-pin',
    html: `
      <div style="
        background-color: ${hex};
        width: 24px;
        height: 24px;
        border-radius: 50% 50% 50% 0;
        transform: rotate(-45deg);
        border: 2px solid #FFFFFF;
        box-shadow: 0 3px 8px rgba(7, 59, 50, 0.35);
        display: flex;
        align-items: center;
        justify-content: center;
      ">
        <div style="
          width: 7px;
          height: 7px;
          background-color: #FFFFFF;
          border-radius: 50%;
        "></div>
      </div>
    `,
    iconSize: [24, 24],
    iconAnchor: [12, 24],
    popupAnchor: [0, -24],
  });
};

export const MAHARASHTRA_CENTER: [number, number] = [19.3, 76.2];
export const MAHARASHTRA_DEFAULT_ZOOM = 7;
export const PUNE_CENTER: [number, number] = [18.5204, 73.8567];
export const PUNE_DEFAULT_ZOOM = 10;

export const getDepthColor = (depth: number | null | undefined): string => {
  if (depth === null || depth === undefined) return '#718078'; // Secondary Text / Slate Gray-Green
  if (depth < 5.0) return '#119B72'; // Shallow (< 5m): Emerald Green (Abundant)
  if (depth < 10.0) return '#0B4F43'; // Moderate (5-10m): Dark Green
  if (depth < 15.0) return '#E9A23B'; // Deep (10-15m): Warning Amber
  return '#E45B55'; // Very Deep (> 15m): Critical Red
};

export const getDepthCategory = (depth: number | null | undefined): string => {
  if (depth === null || depth === undefined) return 'Unevaluated';
  if (depth < 5.0) return 'Shallow (< 5m bgl)';
  if (depth < 10.0) return 'Moderate (5-10m bgl)';
  if (depth < 15.0) return 'Deep (10-15m bgl)';
  return 'Very Deep (> 15m bgl)';
};
