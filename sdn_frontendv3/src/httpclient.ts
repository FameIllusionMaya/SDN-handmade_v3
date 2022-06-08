import axios, { AxiosInstance } from "axios";

const apiClient: AxiosInstance = axios.create({
  baseURL: "http://10.50.34.15:5001/api/v1",
  headers: {
    "Content-type": "application/json",
  },
});

export default apiClient;
