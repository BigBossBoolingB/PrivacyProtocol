import React, { useState, useMemo } from 'react';
import { ChevronDown, ChevronUp, ChevronsUpDown, Search, X } from 'lucide-react';
import { Input } from './input';
import { Button } from './button';
import { useDebounce } from '@/hooks/use-debounce';
import { cn, sortBy, filterBy } from '@/utils';

/**
 * DataTable component for displaying tabular data with sorting, filtering, and pagination
 * 
 * @param {Object} props - Component props
 * @param {Array} props.data - Data to display
 * @param {Array} props.columns - Column definitions
 * @param {string} [props.keyField='id'] - Field to use as key
 * @param {boolean} [props.loading=false] - Whether the data is loading
 * @param {boolean} [props.searchable=true] - Whether the table is searchable
 * @param {boolean} [props.pagination=true] - Whether to show pagination
 * @param {number} [props.pageSize=10] - Number of rows per page
 * @param {string} [props.className] - Additional CSS classes
 * @returns {JSX.Element} - Rendered component
 */
export function DataTable({
  data = [],
  columns = [],
  keyField = 'id',
  loading = false,
  searchable = true,
  pagination = true,
  pageSize = 10,
  className
}) {
  const [searchTerm, setSearchTerm] = useState('');
  const [sortConfig, setSortConfig] = useState({ key: null, direction: 'asc' });
  const [currentPage, setCurrentPage] = useState(1);
  
  // Debounce search term to avoid excessive filtering
  const debouncedSearchTerm = useDebounce(searchTerm, 300);

  // Handle sort
  const handleSort = (key) => {
    let direction = 'asc';
    
    if (sortConfig.key === key) {
      direction = sortConfig.direction === 'asc' ? 'desc' : 'asc';
    }
    
    setSortConfig({ key, direction });
  };

  // Filter and sort data
  const processedData = useMemo(() => {
    let result = [...data];
    
    // Filter by search term
    if (debouncedSearchTerm) {
      result = result.filter(item => {
        return columns.some(column => {
          if (!column.searchable) return false;
          
          const value = column.accessor ? column.accessor(item) : item[column.key];
          
          if (value == null) return false;
          
          return String(value).toLowerCase().includes(debouncedSearchTerm.toLowerCase());
        });
      });
    }
    
    // Sort data
    if (sortConfig.key) {
      result = sortBy(
        result,
        item => {
          const column = columns.find(col => col.key === sortConfig.key);
          return column?.accessor ? column.accessor(item) : item[sortConfig.key];
        },
        sortConfig.direction
      );
    }
    
    return result;
  }, [data, columns, debouncedSearchTerm, sortConfig]);

  // Paginate data
  const paginatedData = useMemo(() => {
    if (!pagination) return processedData;
    
    const startIndex = (currentPage - 1) * pageSize;
    return processedData.slice(startIndex, startIndex + pageSize);
  }, [processedData, currentPage, pageSize, pagination]);

  // Calculate total pages
  const totalPages = useMemo(() => {
    if (!pagination) return 1;
    return Math.max(1, Math.ceil(processedData.length / pageSize));
  }, [processedData, pageSize, pagination]);

  // Handle page change
  const handlePageChange = (page) => {
    setCurrentPage(Math.min(Math.max(1, page), totalPages));
  };

  // Clear search
  const handleClearSearch = () => {
    setSearchTerm('');
  };

  // Render loading state
  if (loading) {
    return (
      <div className="w-full overflow-hidden rounded-lg border border-gray-800/50 bg-gray-900/50">
        <div className="p-4 flex justify-center items-center h-64">
          <div className="animate-pulse space-y-4">
            <div className="h-4 bg-gray-700 rounded w-3/4"></div>
            <div className="h-4 bg-gray-700 rounded w-1/2"></div>
            <div className="h-4 bg-gray-700 rounded w-5/6"></div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={cn("w-full", className)}>
      {/* Search */}
      {searchable && (
        <div className="mb-4 relative">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-500" />
            <Input
              placeholder="Search..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10 bg-gray-900/50 border-gray-800/50"
            />
            {searchTerm && (
              <button
                onClick={handleClearSearch}
                className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-500 hover:text-gray-300"
              >
                <X className="h-4 w-4" />
              </button>
            )}
          </div>
        </div>
      )}

      {/* Table */}
      <div className="w-full overflow-hidden rounded-lg border border-gray-800/50 bg-gray-900/50">
        <div className="w-full overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-800/50 bg-gray-900/80">
                {columns.map((column) => (
                  <th
                    key={column.key}
                    className={cn(
                      "px-4 py-3 text-left text-sm font-medium text-gray-300",
                      column.sortable && "cursor-pointer select-none",
                      column.width && `w-${column.width}`
                    )}
                    onClick={() => column.sortable && handleSort(column.key)}
                  >
                    <div className="flex items-center space-x-1">
                      <span>{column.header}</span>
                      {column.sortable && (
                        <span>
                          {sortConfig.key === column.key ? (
                            sortConfig.direction === 'asc' ? (
                              <ChevronUp className="h-4 w-4" />
                            ) : (
                              <ChevronDown className="h-4 w-4" />
                            )
                          ) : (
                            <ChevronsUpDown className="h-4 w-4 opacity-50" />
                          )}
                        </span>
                      )}
                    </div>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {paginatedData.length === 0 ? (
                <tr>
                  <td
                    colSpan={columns.length}
                    className="px-4 py-8 text-center text-gray-400"
                  >
                    No data available
                  </td>
                </tr>
              ) : (
                paginatedData.map((row) => (
                  <tr
                    key={row[keyField]}
                    className="border-b border-gray-800/50 hover:bg-gray-800/30"
                  >
                    {columns.map((column) => (
                      <td
                        key={`${row[keyField]}-${column.key}`}
                        className="px-4 py-3 text-sm text-gray-300"
                      >
                        {column.cell
                          ? column.cell(row)
                          : column.accessor
                            ? column.accessor(row)
                            : row[column.key]}
                      </td>
                    ))}
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        {pagination && totalPages > 1 && (
          <div className="flex items-center justify-between px-4 py-3 border-t border-gray-800/50">
            <div className="text-sm text-gray-400">
              Showing {Math.min((currentPage - 1) * pageSize + 1, processedData.length)} to{' '}
              {Math.min(currentPage * pageSize, processedData.length)} of {processedData.length} results
            </div>
            <div className="flex space-x-1">
              <Button
                variant="outline"
                size="sm"
                onClick={() => handlePageChange(currentPage - 1)}
                disabled={currentPage === 1}
                className="border-gray-800/50 text-gray-300 hover:bg-gray-800/50"
              >
                Previous
              </Button>
              {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                let pageNum;
                
                if (totalPages <= 5) {
                  pageNum = i + 1;
                } else if (currentPage <= 3) {
                  pageNum = i + 1;
                } else if (currentPage >= totalPages - 2) {
                  pageNum = totalPages - 4 + i;
                } else {
                  pageNum = currentPage - 2 + i;
                }
                
                return (
                  <Button
                    key={pageNum}
                    variant={currentPage === pageNum ? "default" : "outline"}
                    size="sm"
                    onClick={() => handlePageChange(pageNum)}
                    className={cn(
                      "border-gray-800/50",
                      currentPage === pageNum
                        ? "bg-blue-600 text-white hover:bg-blue-700"
                        : "text-gray-300 hover:bg-gray-800/50"
                    )}
                  >
                    {pageNum}
                  </Button>
                );
              })}
              <Button
                variant="outline"
                size="sm"
                onClick={() => handlePageChange(currentPage + 1)}
                disabled={currentPage === totalPages}
                className="border-gray-800/50 text-gray-300 hover:bg-gray-800/50"
              >
                Next
              </Button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}