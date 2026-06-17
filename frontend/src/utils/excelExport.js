import writeExcelFile from 'write-excel-file/browser'

const mapHorizontalAlignment = (value) => {
  if (value === 'center') return 'center'
  if (value === 'right') return 'right'
  return value || undefined
}

const mapVerticalAlignment = (value) => {
  if (value === 'middle') return 'center'
  if (value === 'center') return 'center'
  if (value === 'top') return 'top'
  return value || undefined
}

const toCell = (value, style = {}) => ({
  value: value ?? '',
  fontWeight: style.font?.bold ? 'bold' : undefined,
  align: mapHorizontalAlignment(style.alignment?.horizontal),
  alignVertical: mapVerticalAlignment(style.alignment?.vertical),
  wrap: Boolean(style.alignment?.wrapText),
  backgroundColor: style.fill?.fgColor,
})

export const exportRowsToExcel = async ({
  rows,
  columns = [],
  sheetName = 'Sheet1',
  fileName = 'export.xlsx',
  headerStyle = {},
  bodyStyle = {},
}) => {
  const sheetData = rows.map((row, rowIndex) => {
    const style = rowIndex === 0 ? headerStyle : bodyStyle
    return row.map((cell) => toCell(cell, style))
  })

  await writeExcelFile(sheetData, {
    columns,
    sheet: sheetName,
  }).toFile(fileName)
}
