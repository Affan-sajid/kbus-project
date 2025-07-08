const extractPlaceName = (fullAddress) => {
  if (!fullAddress) return '';
  const commaIdx = fullAddress.indexOf(',');
  if (commaIdx !== -1) return fullAddress.slice(0, commaIdx);
  return fullAddress.split(' ').slice(0, 2).join(' ');
};

export default extractPlaceName; 