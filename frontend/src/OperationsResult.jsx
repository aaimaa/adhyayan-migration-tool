const OperationsResult = ({ socketResult = [] }) => {
  return (
    <div style={{ textAlign: 'center' }}>
      <div style={{  marginTop: '1rem',marginBottom: '2rem', fontSize: '2em' }}>Operations Result</div>
      <table style={{ margin: 'auto', width: '80%', borderCollapse: 'collapse' }}>
        <thead>
          <tr style={{ backgroundColor: '#f2f2f2' }}>
            <th style={{ padding: '10px', textAlign: 'left' }}>S.No.</th>
            <th style={{ padding: '10px', textAlign: 'left' }}>Link</th>
            <th style={{ padding: '10px', textAlign: 'left' }}>Success</th>
          </tr>
        </thead>
        <tbody>
          {socketResult.map(({ link, success }, index) => (
            <tr key={index} style={{ borderBottom: '1px solid #ddd' }}>
              <td style={{ padding: '10px' }}>{index + 1}</td>
              <td style={{ padding: '10px' }}>
                <a href={link} target="_blank" rel="noopener noreferrer" style={{ color: '#007bff', textDecoration: 'none' }}>
                  {link}
                </a>
              </td>
              <td style={{ padding: '10px', color: success ? 'green' : 'red' }}>
                {success ? 'Success' : 'Failed'}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default OperationsResult;
