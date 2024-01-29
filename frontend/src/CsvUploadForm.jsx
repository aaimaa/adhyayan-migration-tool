import { useState, useEffect } from 'react';
import io from 'socket.io-client';
import './CsvUploadForm.css';
import OperationsResult from './OperationsResult';

const CsvUploadForm = () => {
  const [file, setFile] = useState(null);
  const [awsAccessKeyId, setAwsAccessKeyId] = useState('');
  const [awsSecretAccessKey, setAwsSecretAccessKey] = useState('');
  const [regionName, setRegionName] = useState('');
  const [destinationBucket, setDestinationBucket] = useState('');
  const [endpointUrl, setEndpointUrl] = useState('');
  const [sourceLink, setSourceLink] = useState('');
  const [uploadOption, setUploadOption] = useState('csv'); // 'csv' or 'link'
  const [actionOption, setActionOption] = useState('upload'); // 'upload', 'convertResolution', or 'convertToHLS'

  const [socket, setSocket] = useState(null);

  const [socketResult, updateSocketResult] = useState([]);


  // it will Connect to the WebSocket when the component mounts
  useEffect(() => {
    const newSocket = io('http://20.193.144.175');
    setSocket(newSocket);
  
    console.log('WebSocket connected');
  
    // Clean up the WebSocket connection when the component unmounts
    return () => newSocket.disconnect();
  }, []);  

  // it will Listen for the 'operation_complete' event from the server
  useEffect(() => {
    if (socket) {
      socket.on('operation_complete', (data) => {
        console.log('Upload completed for link:', data.link, data.success);
        updateSocketResult(prev => [...prev,
          {
            link: data.link,
            success: data.success
          }])
      });

      console.log('Event listener added for upload_complete');
    }
  }, [socket]);
  
  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0];
    setFile(selectedFile);
  };

  const handleUploadOptionChange = (option) => {
    setUploadOption(option);
    setFile(null);
    setSourceLink('');
  };

  const handleActionOptionChange = (option) => {
    setActionOption(option);
  };

  const handleFormSubmit = async (event) => {
    event.preventDefault();

    const apiUrl = 'http://20.193.144.175';

    let endpoint = '';

    if (uploadOption === 'csv' && file) {
      endpoint =
        actionOption === 'upload'
          ? '/upload-csv'
          : actionOption === 'convertResolution'
          ? '/convert-resolution-csv'
          : actionOption === 'convertToHLS'
          ? '/convert-hsl-csv'
          : '';
    } else if (uploadOption === 'link' && sourceLink) {
      endpoint =
        actionOption === 'upload'
          ? '/upload'
          : actionOption === 'convertResolution'
          ? '/convert-resolution'
          : actionOption === 'convertToHLS'
          ? '/convert-hsl'
          : '';
    } else {
      console.error('Invalid submission. Please select either a CSV file or a source link.');
      return;
    }

    const formData = new FormData();
    formData.append('csv_file', file);
    formData.append('aws_access_key_id', awsAccessKeyId);
    formData.append('aws_secret_access_key', awsSecretAccessKey);
    formData.append('region_name', regionName);
    formData.append('destination_bucket', destinationBucket);
    formData.append('endpoint_url', endpointUrl);
    formData.append('source_link', sourceLink);

    const jsonData = {
      aws_access_key_id: awsAccessKeyId,
      aws_secret_access_key: awsSecretAccessKey,
      region_name: regionName,
      destination_bucket: destinationBucket,
      endpoint_url: endpointUrl,
      source_link: sourceLink,
    };

    formData.append('json_data', JSON.stringify(jsonData));

    try {
      const response = await fetch(apiUrl + endpoint, {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        console.log('Request sent successfully!');
      } else {
        console.error('Request failed.');
      }
    } catch (error) {
      console.error('Error during request:', error);
    }
  };

  return (
  <>  
    <div className="csv-upload-form-container">
      <h2 className='heading'>Video Operations App</h2>
      <form onSubmit={handleFormSubmit} className="upload-form">
        <div className="upload-option">
          <label>
            <input
              type="radio"
              value="csv"
              checked={uploadOption === 'csv'}
              onChange={() => handleUploadOptionChange('csv')}
            />
            Upload CSV File:
          </label>
          {uploadOption === 'csv' && (
            <input type="file" accept=".csv" onChange={handleFileChange} />
          )}
        </div>
        <div className="upload-option">
          <label>
            <input
              type="radio"
              value="link"
              checked={uploadOption === 'link'}
              onChange={() => handleUploadOptionChange('link')}
            />
            Provide Source Link:
          </label>
          {uploadOption === 'link' && (
            <input
              type="text"
              value={sourceLink}
              onChange={(e) => setSourceLink(e.target.value)}
            />
          )}
        </div>

        <div className="action-option">
          <label>Action:</label>
          <select
            value={actionOption}
            onChange={(e) => handleActionOptionChange(e.target.value)}
            className="action-select"
          >
            <option value="upload">Upload to S3/R2</option>
            <option value="convertResolution">Convert Video Resolution</option>
            <option value="convertToHLS">Convert to HLS</option>
          </select>
        </div>

        <div className="input-fields">
          <div className="form-group">
            <label htmlFor="awsAccessKeyId">AWS Access Key ID:</label>
            <input
              type="text"
              id="awsAccessKeyId"
              value={awsAccessKeyId}
              onChange={(e) => setAwsAccessKeyId(e.target.value)}
            />
          </div>
          <div className="form-group">
            <label htmlFor="awsSecretAccessKey">AWS Secret Access Key:</label>
            <input
              type="text"
              id="awsSecretAccessKey"
              value={awsSecretAccessKey}
              onChange={(e) => setAwsSecretAccessKey(e.target.value)}
            />
          </div>
          <div className="form-group">
            <label htmlFor="regionName">Region Name:</label>
            <input
              type="text"
              id="regionName"
              value={regionName}
              onChange={(e) => setRegionName(e.target.value)}
            />
          </div>
          <div className="form-group">
            <label htmlFor="destinationBucket">Destination Bucket:</label>
            <input
              type="text"
              id="destinationBucket"
              value={destinationBucket}
              onChange={(e) => setDestinationBucket(e.target.value)}
            />
          </div>
          <div className="form-group">
            <label htmlFor="endpointUrl">Endpoint URL:</label>
            <input
              type="text"
              id="endpointUrl"
              value={endpointUrl}
              onChange={(e) => setEndpointUrl(e.target.value)}
            />
          </div>
        </div>

        <div className="submit-button">
          <button type="submit">Submit</button>
        </div>
      </form>
    </div>
    <OperationsResult socketResult= {socketResult} />
  </>
  );
};

export default CsvUploadForm;
