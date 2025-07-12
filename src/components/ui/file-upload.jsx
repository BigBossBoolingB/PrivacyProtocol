import React, { useState, useRef } from 'react';
import { Upload, X, File, AlertCircle, CheckCircle2 } from 'lucide-react';
import { Button } from './button';
import { Progress } from './progress';
import { cn, formatFileSize } from '@/utils';

/**
 * FileUpload component for handling file uploads with drag and drop
 * 
 * @param {Object} props - Component props
 * @param {Function} props.onUpload - Callback when files are uploaded
 * @param {string[]} [props.acceptedFileTypes] - Accepted file types (e.g., '.pdf', 'image/*')
 * @param {number} [props.maxFileSize=5242880] - Maximum file size in bytes (default: 5MB)
 * @param {number} [props.maxFiles=1] - Maximum number of files
 * @param {boolean} [props.multiple=false] - Whether to allow multiple files
 * @param {string} [props.className] - Additional CSS classes
 * @returns {JSX.Element} - Rendered component
 */
export function FileUpload({
  onUpload,
  acceptedFileTypes,
  maxFileSize = 5 * 1024 * 1024, // 5MB
  maxFiles = 1,
  multiple = false,
  className
}) {
  const [files, setFiles] = useState([]);
  const [isDragging, setIsDragging] = useState(false);
  const [errors, setErrors] = useState([]);
  const [uploadProgress, setUploadProgress] = useState({});
  const fileInputRef = useRef(null);

  // Handle file selection
  const handleFileSelect = (selectedFiles) => {
    const newErrors = [];
    const newFiles = [...files];
    
    // Check if adding these files would exceed the maximum
    if (newFiles.length + selectedFiles.length > maxFiles) {
      newErrors.push(`You can only upload up to ${maxFiles} file${maxFiles === 1 ? '' : 's'}`);
      return;
    }
    
    // Validate each file
    Array.from(selectedFiles).forEach(file => {
      // Check file type
      if (acceptedFileTypes && acceptedFileTypes.length > 0) {
        const fileType = file.type;
        const fileExtension = `.${file.name.split('.').pop().toLowerCase()}`;
        const isAccepted = acceptedFileTypes.some(type => {
          if (type.startsWith('.')) {
            return fileExtension === type.toLowerCase();
          }
          return fileType.match(new RegExp(type.replace('*', '.*')));
        });
        
        if (!isAccepted) {
          newErrors.push(`File "${file.name}" has an invalid type. Accepted types: ${acceptedFileTypes.join(', ')}`);
          return;
        }
      }
      
      // Check file size
      if (file.size > maxFileSize) {
        newErrors.push(`File "${file.name}" exceeds the maximum size of ${formatFileSize(maxFileSize)}`);
        return;
      }
      
      // Add file to list
      newFiles.push(file);
    });
    
    setFiles(newFiles);
    setErrors(newErrors);
    
    // If no errors and files were added, call onUpload
    if (newErrors.length === 0 && newFiles.length > files.length) {
      handleUpload(newFiles);
    }
  };

  // Handle file upload
  const handleUpload = async (filesToUpload) => {
    if (!onUpload) return;
    
    try {
      // Simulate upload progress
      const simulateProgress = () => {
        const progress = {};
        
        filesToUpload.forEach(file => {
          progress[file.name] = 0;
        });
        
        setUploadProgress(progress);
        
        const interval = setInterval(() => {
          setUploadProgress(prev => {
            const newProgress = { ...prev };
            let allComplete = true;
            
            Object.keys(newProgress).forEach(fileName => {
              if (newProgress[fileName] < 100) {
                newProgress[fileName] += 5;
                allComplete = false;
              }
            });
            
            if (allComplete) {
              clearInterval(interval);
            }
            
            return newProgress;
          });
        }, 200);
        
        return interval;
      };
      
      const progressInterval = simulateProgress();
      
      // Call the onUpload callback
      await onUpload(multiple ? filesToUpload : filesToUpload[0]);
      
      // Clear the interval if it's still running
      clearInterval(progressInterval);
      
      // Set all progress to 100%
      const completeProgress = {};
      filesToUpload.forEach(file => {
        completeProgress[file.name] = 100;
      });
      setUploadProgress(completeProgress);
      
    } catch (error) {
      console.error('Upload error:', error);
      setErrors([...errors, `Upload failed: ${error.message || 'Unknown error'}`]);
    }
  };

  // Handle drag events
  const handleDragEnter = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFileSelect(e.dataTransfer.files);
    }
  };

  // Handle click on the dropzone
  const handleDropzoneClick = () => {
    fileInputRef.current?.click();
  };

  // Handle file input change
  const handleFileInputChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      handleFileSelect(e.target.files);
    }
  };

  // Remove a file
  const handleRemoveFile = (fileToRemove) => {
    setFiles(files.filter(file => file !== fileToRemove));
    
    // Remove from progress
    setUploadProgress(prev => {
      const newProgress = { ...prev };
      delete newProgress[fileToRemove.name];
      return newProgress;
    });
  };

  // Clear all files
  const handleClearFiles = () => {
    setFiles([]);
    setUploadProgress({});
  };

  return (
    <div className={cn("space-y-4", className)}>
      {/* File input (hidden) */}
      <input
        ref={fileInputRef}
        type="file"
        accept={acceptedFileTypes?.join(',')}
        multiple={multiple}
        className="hidden"
        onChange={handleFileInputChange}
      />
      
      {/* Dropzone */}
      <div
        className={cn(
          "border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-colors",
          isDragging
            ? "border-blue-500 bg-blue-500/10"
            : "border-gray-700 hover:border-gray-600 bg-gray-900/50",
          files.length > 0 && "border-green-500/50 bg-green-500/5"
        )}
        onDragEnter={handleDragEnter}
        onDragLeave={handleDragLeave}
        onDragOver={handleDragOver}
        onDrop={handleDrop}
        onClick={handleDropzoneClick}
      >
        <div className="flex flex-col items-center justify-center space-y-3">
          <div className={cn(
            "p-3 rounded-full",
            isDragging
              ? "bg-blue-500/20 text-blue-400"
              : files.length > 0
                ? "bg-green-500/20 text-green-400"
                : "bg-gray-800 text-gray-400"
          )}>
            <Upload className="h-6 w-6" />
          </div>
          
          <div className="space-y-1">
            <p className="text-sm font-medium text-gray-300">
              {isDragging
                ? "Drop files here"
                : files.length > 0
                  ? `${files.length} file${files.length === 1 ? '' : 's'} selected`
                  : "Drag and drop files here or click to browse"}
            </p>
            
            <p className="text-xs text-gray-500">
              {acceptedFileTypes
                ? `Accepted file types: ${acceptedFileTypes.join(', ')}`
                : "All file types accepted"}
            </p>
            
            <p className="text-xs text-gray-500">
              Maximum file size: {formatFileSize(maxFileSize)}
            </p>
          </div>
        </div>
      </div>
      
      {/* Error messages */}
      {errors.length > 0 && (
        <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-3">
          <div className="flex items-start space-x-2">
            <AlertCircle className="h-5 w-5 text-red-500 mt-0.5" />
            <div className="space-y-1">
              {errors.map((error, index) => (
                <p key={index} className="text-sm text-red-400">
                  {error}
                </p>
              ))}
            </div>
          </div>
        </div>
      )}
      
      {/* File list */}
      {files.length > 0 && (
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <h4 className="text-sm font-medium text-gray-300">
              Selected Files
            </h4>
            <Button
              variant="ghost"
              size="sm"
              onClick={handleClearFiles}
              className="text-gray-400 hover:text-gray-300"
            >
              Clear All
            </Button>
          </div>
          
          <div className="space-y-2">
            {files.map((file, index) => (
              <div
                key={index}
                className="flex items-center justify-between p-3 bg-gray-800/50 rounded-lg border border-gray-700/50"
              >
                <div className="flex items-center space-x-3">
                  <div className="p-2 bg-gray-700/50 rounded">
                    <File className="h-4 w-4 text-gray-400" />
                  </div>
                  <div className="space-y-1">
                    <p className="text-sm font-medium text-gray-300 truncate max-w-[200px]">
                      {file.name}
                    </p>
                    <p className="text-xs text-gray-500">
                      {formatFileSize(file.size)}
                    </p>
                  </div>
                </div>
                
                <div className="flex items-center space-x-3">
                  {uploadProgress[file.name] !== undefined && (
                    <div className="flex items-center space-x-2">
                      {uploadProgress[file.name] === 100 ? (
                        <CheckCircle2 className="h-4 w-4 text-green-500" />
                      ) : (
                        <div className="w-16">
                          <Progress value={uploadProgress[file.name]} className="h-1.5" />
                        </div>
                      )}
                    </div>
                  )}
                  
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => handleRemoveFile(file)}
                    className="h-8 w-8 text-gray-400 hover:text-red-400"
                  >
                    <X className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}