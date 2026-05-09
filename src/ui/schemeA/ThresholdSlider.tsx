import React from 'react';

type ThresholdSliderProps = {
  value: number; // 0.0 - 1.0
  onChange: (v: number) => void;
  'aria-label'?: string;
};

// ThresholdSlider scaffolding for Scheme A
export const ThresholdSlider: React.FC<ThresholdSliderProps> = ({ value, onChange, ...rest }) => {
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = parseFloat(e.target.value);
    if (!Number.isNaN(val)) {
      onChange(val);
    }
  };

  return (
    <div className="threshold-slider" aria-label={rest['aria-label'] || 'Threshold slider for sim_top1_th'}>
      <input
        type="range"
        min={0.0}
        max={1.0}
        step={0.01}
        value={value}
        onChange={handleChange}
        aria-valuemin={0}
        aria-valuemax={1}
        aria-valuenow={value}
        aria-label="sim_top1_th"
      />
      <span className="threshold-value" style={{ display: 'inline-block', width: 60, textAlign: 'right', marginLeft: 8 }}>
        {value.toFixed(2)}
      </span>
    </div>
  );
};

export default ThresholdSlider;
