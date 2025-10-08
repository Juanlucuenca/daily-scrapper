-- Tabla para almacenar datos financieros
CREATE TABLE IF NOT EXISTS financial_data (
    id BIGSERIAL PRIMARY KEY,
    tipo VARCHAR(50) NOT NULL,  -- 'uva', 'dolar_mayorista', 'dolar_mep'
    fecha VARCHAR(20) NOT NULL,
    valor DECIMAL(10, 2) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    UNIQUE(tipo, fecha)
);

-- Índices para mejorar performance
CREATE INDEX IF NOT EXISTS idx_financial_data_tipo ON financial_data(tipo);
CREATE INDEX IF NOT EXISTS idx_financial_data_fecha ON financial_data(fecha);
CREATE INDEX IF NOT EXISTS idx_financial_data_tipo_fecha ON financial_data(tipo, fecha);

-- Función para actualizar updated_at automáticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = TIMEZONE('utc'::text, NOW());
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger para actualizar updated_at
CREATE TRIGGER update_financial_data_updated_at BEFORE UPDATE ON financial_data
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Comentarios
COMMENT ON TABLE financial_data IS 'Almacena datos históricos de valores financieros (UVA, Dólar Mayorista, Dólar MEP)';
COMMENT ON COLUMN financial_data.tipo IS 'Tipo de valor financiero: uva, dolar_mayorista, dolar_mep';
COMMENT ON COLUMN financial_data.fecha IS 'Fecha en formato dd-mm-yy';
COMMENT ON COLUMN financial_data.valor IS 'Valor del indicador financiero';
