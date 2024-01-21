import axios from 'axios';
import { useState } from 'react';

const VideoOperationsForm = () => {
  const [formData, setFormData] = useState({
    aws_access_key_id: '',
    aws_secret_access_key: '',
    endpoint_url: import.meta.env.VITE_API_URL || 'http://127.0.0.1:5000',
    destination_bucket: '',
    region_name: '',
    source_link: '',
    csv_file: null,
    operation: 'upload', // Default to 'upload'
  });

  const handleInputChange = (e) => {
    const { name, value, type, files } = e.target;

    setFormData((prevData) => ({
      ...prevData,
      [name]: type === 'file' ? files[0] : value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      const apiUrl = formData.endpoint_url;

      const formDataToSubmit = new FormData();

      // Append form data to FormData object
      Object.entries(formData).forEach(([key, value]) => {
        formDataToSubmit.append(key, value);
      });

      if (formData.operation === 'upload') {
        await axios.post(`${apiUrl}/upload`, formDataToSubmit);
      } else if (formData.operation === 'convert-resolution') {
        await axios.post(`${apiUrl}/convert-resolution`, formDataToSubmit);
      } else if (formData.operation === 'convert-hsl') {
        await axios.post(`${apiUrl}/convert-hsl`, formDataToSubmit);
      } else {
        // Handle other operations if needed
      }

      // Reset the form after successful submission
      setFormData({
        aws_access_key_id: '',
        aws_secret_access_key: '',
        endpoint_url: import.meta.env.VITE_API_URL || 'http://127.0.0.1:5000',
        destination_bucket: '',
        region_name: '',
        source_link: '',
        csv_file: null,
        operation: 'upload',
      });

      // Provide feedback to the user (e.g., success message)
      console.log('Form submitted successfully!');
    } catch (error) {
      // Handle errors (e.g., display error message)
      console.error('API Request Error:', error.message || error);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
        <label>
          AWS Access Key ID:
          <input type="text" name="aws_access_key_id" value={formData.aws_access_key_id} onChange={handleInputChange} required />
        </label>

        <label>
          AWS Secret Access Key:
          <input type="text" name="aws_secret_access_key" value={formData.aws_secret_access_key} onChange={handleInputChange} required />
        </label>

        <label>
          Endpoint URL:
          <input type="text" name="endpoint_url" value={formData.endpoint_url} onChange={handleInputChange} />
        </label>

        <label>
          Destination Bucket:
          <input type="text" name="destination_bucket" value={formData.destination_bucket} onChange={handleInputChange} required />
        </label>

        <label>
          Region Name:
          <input type="text" name="region_name" value={formData.region_name} onChange={handleInputChange} required />
        </label>

        <label>
          Operation:
          <select name="operation" value={formData.operation} onChange={handleInputChange}>
            <option value="upload">Upload</option>
            <option value="convert-resolution">Convert Resolution</option>
            <option value="convert-hsl">Convert to HSL</option>
          </select>
        </label>

        {formData.operation === 'upload' && (
          <label>
            Source Link:
            <input type="text" name="source_link" value={formData.source_link} onChange={handleInputChange} required />
          </label>
        )}

        {formData.operation !== 'upload' && (
          <label>
            CSV File:
            <input type="file" name="csv_file" onChange={handleInputChange} accept=".csv" required />
          </label>
        )}

        <button type="submit">Submit</button>
    </form>
  );
};

export default VideoOperationsForm;
