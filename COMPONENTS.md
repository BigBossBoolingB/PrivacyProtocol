# Component Documentation

> **Comprehensive reference for all React components in the Privacy Protocol application**

## Table of Contents

- [Component Overview](#component-overview)
- [Analyzer Components](#analyzer-components)
- [Dashboard Components](#dashboard-components)
- [History Components](#history-components)
- [Insights Components](#insights-components)
- [Subscription Components](#subscription-components)
- [UI Components](#ui-components)
- [Usage Patterns](#usage-patterns)
- [Component Guidelines](#component-guidelines)

## Component Overview

The Privacy Protocol application contains **50+ React components** organized into 6 main categories. Each component follows consistent patterns for props, state management, and API integration.

### Component Categories

1. **Analyzer Components** (3 components) - Privacy policy analysis workflow
2. **Dashboard Components** (4 components) - User overview and insights
3. **History Components** (3 components) - Historical data management
4. **Insights Components** (4 components) - Community analytics and trends
5. **Subscription Components** (3 components) - Payment and subscription management
6. **UI Components** (30+ components) - Reusable component library

### Common Props Pattern

Most components follow this prop structure:

```typescript
interface ComponentProps {
  // Data props
  data?: any;
  loading?: boolean;
  error?: Error | null;
  
  // Event handlers
  onAction?: () => void;
  onChange?: (value: any) => void;
  
  // UI customization
  className?: string;
  variant?: 'default' | 'secondary' | 'destructive';
  size?: 'sm' | 'md' | 'lg';
  
  // Feature flags
  disabled?: boolean;
  readonly?: boolean;
}
```

## Analyzer Components

### AnalysisResults

**Purpose**: Displays comprehensive privacy policy analysis results with risk scores, flagged clauses, and recommendations.

**Location**: `src/components/analyzer/AnalysisResults.jsx`

**Props**:
```typescript
interface AnalysisResultsProps {
  agreement: PrivacyAgreement;     // Analysis data from Base44 API
  onExport?: () => void;           // Export results handler
  onSaveToHistory?: () => void;    // Save to history handler
  className?: string;
}
```

**Key Features**:
- Risk score visualization with color-coded indicators
- Flagged clauses with severity levels and explanations
- Data collection breakdown by category
- User rights summary with actionable information
- Third-party tracker identification
- Personalized recommendations

**Usage Example**:
```jsx
import { AnalysisResults } from '@/components/analyzer';

function AnalyzerPage() {
  const { data: agreement } = useApiQuery('getAnalysis', analysisId);
  
  return (
    <AnalysisResults
      agreement={agreement}
      onExport={() => exportToPDF(agreement)}
      onSaveToHistory={() => saveAnalysis(agreement)}
    />
  );
}
```

**Data Structure**:
```typescript
interface PrivacyAgreement {
  id: string;
  title: string;
  company_name: string;
  risk_score: number;                    // 0-100
  flagged_clauses: FlaggedClause[];
  data_collection_breakdown: DataBreakdown;
  user_rights_summary: UserRights;
  third_party_trackers: string[];
  recommendations: Recommendation[];
}
```

### FileUploadZone

**Purpose**: Drag-and-drop file upload interface for privacy policy documents.

**Location**: `src/components/analyzer/FileUploadZone.jsx`

**Props**:
```typescript
interface FileUploadZoneProps {
  onFileSelect: (file: File) => void;    // File selection handler
  onAnalyze: (content: string) => void;  // Analysis trigger
  acceptedTypes?: string[];              // Allowed file types
  maxSize?: number;                      // Max file size in bytes
  disabled?: boolean;
  className?: string;
}
```

**Key Features**:
- Drag-and-drop file upload
- File type validation (PDF, DOC, DOCX, TXT)
- File size validation and progress indication
- Content extraction and preprocessing
- Error handling for unsupported files

**Usage Example**:
```jsx
import { FileUploadZone } from '@/components/analyzer';

function AnalyzerPage() {
  const handleFileAnalysis = async (content) => {
    const result = await analyzePolicy({ content });
    setAnalysisResult(result);
  };

  return (
    <FileUploadZone
      onAnalyze={handleFileAnalysis}
      acceptedTypes={['pdf', 'doc', 'docx', 'txt']}
      maxSize={10 * 1024 * 1024} // 10MB
    />
  );
}
```

### URLAnalyzer

**Purpose**: URL-based privacy policy analysis input with automatic content extraction.

**Location**: `src/components/analyzer/URLAnalyzer.jsx`

**Props**:
```typescript
interface URLAnalyzerProps {
  onAnalyze: (url: string) => void;      // URL analysis handler
  onContentExtracted?: (content: string) => void;
  placeholder?: string;
  disabled?: boolean;
  className?: string;
}
```

**Key Features**:
- URL validation and formatting
- Automatic content extraction from web pages
- Loading states during content fetch
- Error handling for inaccessible URLs
- Preview of extracted content

**Usage Example**:
```jsx
import { URLAnalyzer } from '@/components/analyzer';

function AnalyzerPage() {
  const handleURLAnalysis = async (url) => {
    const content = await extractContentFromURL(url);
    const result = await analyzePolicy({ url, content });
    setAnalysisResult(result);
  };

  return (
    <URLAnalyzer
      onAnalyze={handleURLAnalysis}
      placeholder="Enter privacy policy URL..."
    />
  );
}
```

## Dashboard Components

### PrivacyInsights

**Purpose**: Generates personalized privacy recommendations based on user's analysis history and privacy profile.

**Location**: `src/components/dashboard/PrivacyInsights.jsx`

**Props**:
```typescript
interface PrivacyInsightsProps {
  userProfile: UserPrivacyProfile;       // User preferences and settings
  recentAnalyses: PrivacyAgreement[];    // Recent analysis data
  onUpdateProfile?: (profile: UserPrivacyProfile) => void;
  className?: string;
}
```

**Key Features**:
- Personalized privacy recommendations
- Risk trend analysis over time
- Privacy tolerance matching
- Actionable improvement suggestions
- Integration with user privacy profile

**Usage Example**:
```jsx
import { PrivacyInsights } from '@/components/dashboard';

function Dashboard() {
  const { data: profile } = useApiQuery('getUserProfile');
  const { data: analyses } = useApiQuery('getRecentAnalyses');

  return (
    <PrivacyInsights
      userProfile={profile}
      recentAnalyses={analyses}
      onUpdateProfile={updateUserProfile}
    />
  );
}
```

### RiskTrends

**Purpose**: Visualizes privacy risk trends over time with interactive charts.

**Location**: `src/components/dashboard/RiskTrends.jsx`

**Props**:
```typescript
interface RiskTrendsProps {
  data: RiskTrendData[];                 // Historical risk data
  timeRange?: '7d' | '30d' | '90d' | '1y';
  onTimeRangeChange?: (range: string) => void;
  showComparison?: boolean;              // Show industry comparison
  className?: string;
}
```

**Key Features**:
- Interactive line charts with Recharts
- Multiple time range options
- Industry benchmark comparison
- Risk category breakdown
- Trend analysis and insights

### StatsCard

**Purpose**: Displays key privacy metrics in a card format.

**Location**: `src/components/dashboard/StatsCard.jsx`

**Props**:
```typescript
interface StatsCardProps {
  title: string;
  value: string | number;
  change?: number;                       // Percentage change
  trend?: 'up' | 'down' | 'neutral';
  icon?: React.ComponentType;
  description?: string;
  className?: string;
}
```

**Usage Example**:
```jsx
import { StatsCard } from '@/components/dashboard';
import { Shield } from 'lucide-react';

function Dashboard() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
      <StatsCard
        title="Total Agreements"
        value={42}
        change={12}
        trend="up"
        icon={Shield}
        description="Privacy policies analyzed"
      />
    </div>
  );
}
```

### RecentAnalyses

**Purpose**: Shows a list of recent privacy policy analyses with quick actions.

**Location**: `src/components/dashboard/RecentAnalyses.jsx`

**Props**:
```typescript
interface RecentAnalysesProps {
  analyses: PrivacyAgreement[];
  limit?: number;                        // Number of items to display
  onViewDetails?: (id: string) => void;  // View analysis details
  onReanalyze?: (id: string) => void;    // Trigger reanalysis
  className?: string;
}
```

**Key Features**:
- Chronological list of recent analyses
- Quick action buttons for each analysis
- Risk score indicators and company logos
- Pagination for large datasets
- Loading states and empty state handling

**Usage Example**:
```jsx
import { RecentAnalyses } from '@/components/dashboard';

function Dashboard() {
  const { data: analyses } = useApiQuery('getRecentAnalyses');
  
  return (
    <RecentAnalyses
      analyses={analyses}
      limit={5}
      onViewDetails={(id) => navigate(`/analysis/${id}`)}
      onReanalyze={triggerReanalysis}
    />
  );
}
```

## History Components

### AgreementModal

**Purpose**: Detailed modal view for individual privacy agreements with comprehensive analysis results.

**Location**: `src/components/history/AgreementModal.jsx`

**Props**:
```typescript
interface AgreementModalProps {
  agreement: PrivacyAgreement;
  isOpen: boolean;
  onClose: () => void;
  onExport?: () => void;
  onDelete?: (id: string) => void;
  className?: string;
}
```

**Key Features**:
- Full-screen modal with detailed analysis
- Tabbed interface for different analysis sections
- Export functionality (PDF, JSON)
- Delete and archive options
- Responsive design for mobile devices

**Usage Example**:
```jsx
import { AgreementModal } from '@/components/history';

function HistoryPage() {
  const [selectedAgreement, setSelectedAgreement] = useState(null);
  
  return (
    <>
      <AgreementModal
        agreement={selectedAgreement}
        isOpen={!!selectedAgreement}
        onClose={() => setSelectedAgreement(null)}
        onExport={() => exportAgreement(selectedAgreement)}
      />
    </>
  );
}
```

### AgreementCard

**Purpose**: Summary card component for displaying individual agreements in lists.

**Location**: `src/components/history/AgreementCard.jsx`

**Props**:
```typescript
interface AgreementCardProps {
  agreement: PrivacyAgreement;
  onClick?: () => void;
  onQuickAction?: (action: string) => void;
  showActions?: boolean;
  variant?: 'default' | 'compact';
  className?: string;
}
```

**Key Features**:
- Compact agreement summary display
- Risk score visualization
- Quick action menu (view, export, delete)
- Company branding and logos
- Hover states and animations

### HistoryFilters

**Purpose**: Filtering and search interface for historical analysis data.

**Location**: `src/components/history/HistoryFilters.jsx`

**Props**:
```typescript
interface HistoryFiltersProps {
  onFilterChange: (filters: FilterOptions) => void;
  onSearchChange: (query: string) => void;
  initialFilters?: FilterOptions;
  className?: string;
}

interface FilterOptions {
  dateRange?: [Date, Date];
  riskLevel?: 'low' | 'medium' | 'high';
  company?: string;
  agreementType?: string;
}
```

**Key Features**:
- Advanced search with debounced input
- Date range picker for temporal filtering
- Risk level and company filtering
- Agreement type categorization
- Filter persistence and URL state

## Insights Components

### GlobalPrivacyTrends

**Purpose**: Displays industry-wide privacy trends and benchmarking data.

**Location**: `src/components/insights/GlobalPrivacyTrends.jsx`

**Props**:
```typescript
interface GlobalPrivacyTrendsProps {
  data: TrendData[];
  timeframe?: 'month' | 'quarter' | 'year';
  onTimeframeChange?: (timeframe: string) => void;
  showComparison?: boolean;
  className?: string;
}
```

**Key Features**:
- Interactive trend visualization
- Industry comparison metrics
- Geographic privacy trend mapping
- Regulatory impact analysis
- Exportable trend reports

### CommunityStats

**Purpose**: Community comparison metrics and privacy benchmarking.

**Location**: `src/components/insights/CommunityStats.jsx`

**Props**:
```typescript
interface CommunityStatsProps {
  userStats: UserStats;
  communityStats: CommunityStats;
  onUpdatePreferences?: () => void;
  className?: string;
}
```

**Key Features**:
- User vs. community comparison
- Privacy tolerance benchmarking
- Anonymous community insights
- Personalized recommendations
- Privacy score percentile ranking

### IndustryInsights

**Purpose**: Sector-specific privacy analysis and industry trends.

**Location**: `src/components/insights/IndustryInsights.jsx`

**Props**:
```typescript
interface IndustryInsightsProps {
  industry: string;
  insights: IndustryInsight[];
  onIndustryChange?: (industry: string) => void;
  className?: string;
}
```

**Key Features**:
- Industry-specific privacy analysis
- Regulatory compliance tracking
- Sector risk assessment
- Best practice recommendations
- Competitive privacy analysis

### TrendingRisks

**Purpose**: Displays emerging privacy risks and threat intelligence.

**Location**: `src/components/insights/TrendingRisks.jsx`

**Props**:
```typescript
interface TrendingRisksProps {
  risks: TrendingRisk[];
  onRiskClick?: (risk: TrendingRisk) => void;
  severity?: 'all' | 'high' | 'critical';
  className?: string;
}
```

**Key Features**:
- Real-time risk intelligence
- Severity-based risk categorization
- Actionable risk mitigation advice
- Risk trend analysis
- Alert subscription management

## Subscription Components

### SubscriptionModal

**Purpose**: Subscription upgrade interface with payment processing.

**Location**: `src/components/subscription/SubscriptionModal.jsx`

**Props**:
```typescript
interface SubscriptionModalProps {
  isOpen: boolean;
  onClose: () => void;
  currentPlan?: SubscriptionPlan;
  onUpgrade?: (plan: SubscriptionPlan) => void;
  className?: string;
}
```

**Key Features**:
- Plan comparison and selection
- Stripe and PayPal payment integration
- Usage limit explanations
- Billing cycle management
- Upgrade confirmation flow

### UsageTracker

**Purpose**: Displays subscription usage limits and consumption metrics.

**Location**: `src/components/subscription/UsageTracker.jsx`

**Props**:
```typescript
interface UsageTrackerProps {
  usage: UsageData;
  limits: UsageLimits;
  onUpgrade?: () => void;
  showDetails?: boolean;
  className?: string;
}
```

**Key Features**:
- Real-time usage monitoring
- Visual progress indicators
- Usage history and trends
- Limit warnings and notifications
- Upgrade prompts and recommendations

### UpgradePrompt

**Purpose**: Premium feature promotion and upgrade encouragement.

**Location**: `src/components/subscription/UpgradePrompt.jsx`

**Props**:
```typescript
interface UpgradePromptProps {
  feature: string;
  onUpgrade: () => void;
  onDismiss?: () => void;
  variant?: 'banner' | 'modal' | 'inline';
  className?: string;
}
```

**Key Features**:
- Context-aware upgrade prompts
- Feature benefit highlighting
- A/B tested messaging
- Dismissible notifications
- Conversion tracking

## UI Components

The Privacy Protocol application includes a comprehensive UI component library with 30+ reusable components built on Radix UI primitives and styled with Tailwind CSS.

### Form Components

#### Button
**Location**: `src/components/ui/button.jsx`
```typescript
interface ButtonProps {
  variant?: 'default' | 'destructive' | 'outline' | 'secondary' | 'ghost' | 'link';
  size?: 'default' | 'sm' | 'lg' | 'icon';
  disabled?: boolean;
  loading?: boolean;
  children: React.ReactNode;
}
```

#### Input
**Location**: `src/components/ui/input.jsx`
```typescript
interface InputProps {
  type?: string;
  placeholder?: string;
  disabled?: boolean;
  error?: string;
  className?: string;
}
```

#### Form
**Location**: `src/components/ui/form.jsx`
- Form field wrapper with validation
- Error message display
- Label and description support
- Integration with React Hook Form

### Layout Components

#### Card
**Location**: `src/components/ui/card.jsx`
```typescript
interface CardProps {
  children: React.ReactNode;
  className?: string;
}
```

#### Dialog
**Location**: `src/components/ui/dialog.jsx`
- Modal dialog with overlay
- Accessible keyboard navigation
- Customizable sizes and positions
- Animation and transition support

#### Accordion
**Location**: `src/components/ui/accordion.jsx`
- Collapsible content sections
- Single or multiple expansion
- Smooth animations
- Keyboard navigation

### Data Display Components

#### DataTable
**Location**: `src/components/ui/data-table.jsx`
```typescript
interface DataTableProps {
  columns: ColumnDef[];
  data: any[];
  pagination?: boolean;
  sorting?: boolean;
  filtering?: boolean;
}
```

#### Chart
**Location**: `src/components/ui/chart.jsx`
- Recharts integration wrapper
- Consistent theming and styling
- Responsive design
- Multiple chart types support

#### Badge
**Location**: `src/components/ui/badge.jsx`
```typescript
interface BadgeProps {
  variant?: 'default' | 'secondary' | 'destructive' | 'outline';
  children: React.ReactNode;
}
```

### Navigation Components

#### NavigationMenu
**Location**: `src/components/ui/navigation-menu.jsx`
- Accessible dropdown navigation
- Keyboard and mouse interaction
- Nested menu support
- Mobile-responsive design

#### Breadcrumb
**Location**: `src/components/ui/breadcrumb.jsx`
- Hierarchical navigation display
- Customizable separators
- Link and text items
- Overflow handling

### Feedback Components

#### Alert
**Location**: `src/components/ui/alert.jsx`
```typescript
interface AlertProps {
  variant?: 'default' | 'destructive';
  title?: string;
  description?: string;
  children?: React.ReactNode;
}
```

#### LoadingSpinner
**Location**: `src/components/ui/loading-spinner.jsx`
- Consistent loading indicators
- Multiple sizes and variants
- Accessibility support
- Smooth animations

#### Progress
**Location**: `src/components/ui/progress.jsx`
- Progress bar with percentage
- Animated transitions
- Color variants for different states
- Accessibility labels

## Usage Patterns

### Common Component Patterns

#### 1. Data Fetching Pattern
```jsx
function ComponentWithData() {
  const { data, loading, error } = useApiQuery('endpoint');
  
  if (loading) return <LoadingSpinner />;
  if (error) return <Alert variant="destructive" description={error.message} />;
  
  return <DataDisplay data={data} />;
}
```

#### 2. Form Handling Pattern
```jsx
function FormComponent() {
  const form = useForm({
    resolver: zodResolver(schema),
    defaultValues: {}
  });
  
  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)}>
        <FormField
          control={form.control}
          name="field"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Label</FormLabel>
              <FormControl>
                <Input {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
      </form>
    </Form>
  );
}
```

#### 3. Modal Pattern
```jsx
function ComponentWithModal() {
  const [isOpen, setIsOpen] = useState(false);
  
  return (
    <>
      <Button onClick={() => setIsOpen(true)}>Open Modal</Button>
      <Dialog open={isOpen} onOpenChange={setIsOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Modal Title</DialogTitle>
          </DialogHeader>
        </DialogContent>
      </Dialog>
    </>
  );
}
```

### State Management Patterns

#### 1. Context Usage
```jsx
function ComponentUsingContext() {
  const { user } = useAuth();
  const { subscription } = useSubscription();
  const { showNotification } = useNotification();
  
  return <div>Component content</div>;
}
```

#### 2. API Integration
```jsx
function ComponentWithAPI() {
  const { mutate: updateData, loading } = useApiMutation('updateEndpoint');
  
  const handleUpdate = async (data) => {
    try {
      await updateData(data);
      showNotification('Update successful', 'success');
    } catch (error) {
      showNotification('Update failed', 'error');
    }
  };
  
  return <Button onClick={handleUpdate} loading={loading}>Update</Button>;
}
```

## Component Guidelines

### 1. Component Design Principles

- **Single Responsibility**: Each component has one clear purpose
- **Composition over Inheritance**: Build complex UIs by composing simple components
- **Accessibility First**: All components include proper ARIA labels and keyboard navigation
- **Performance Optimized**: Use React.memo, useMemo, and useCallback appropriately
- **Type Safety**: All components have TypeScript interfaces for props

### 2. Styling Guidelines

- **Tailwind CSS**: Use utility classes for styling
- **Design System**: Follow consistent spacing, colors, and typography
- **Responsive Design**: Mobile-first responsive design approach
- **Dark Mode**: Support for light and dark themes
- **Animation**: Subtle animations for better user experience

### 3. Testing Guidelines

- **Unit Tests**: Test component behavior and props
- **Integration Tests**: Test component interactions
- **Accessibility Tests**: Verify ARIA compliance and keyboard navigation
- **Visual Tests**: Screenshot testing for UI consistency
- **Performance Tests**: Monitor rendering performance

### 4. Documentation Standards

- **JSDoc Comments**: Document all props and component purpose
- **Usage Examples**: Provide clear usage examples
- **Props Interface**: TypeScript interfaces for all props
- **Storybook Stories**: Interactive component documentation
- **Accessibility Notes**: Document accessibility features and requirements

---

## Component Development Workflow

### 1. Creating New Components

```bash
# Create component file
touch src/components/feature/ComponentName.jsx

# Create test file
touch src/components/feature/ComponentName.test.jsx

# Create story file (if using Storybook)
touch src/components/feature/ComponentName.stories.jsx
```

### 2. Component Template

```jsx
import React from 'react';
import { cn } from '@/utils';

interface ComponentNameProps {
  className?: string;
  children?: React.ReactNode;
}

export function ComponentName({ 
  className,
  children,
  ...props 
}: ComponentNameProps) {
  return (
    <div className={cn('base-styles', className)} {...props}>
      {children}
    </div>
  );
}

ComponentName.displayName = 'ComponentName';
```

### 3. Export Pattern

```javascript
// src/components/feature/index.js
export { ComponentName } from './ComponentName';
export { AnotherComponent } from './AnotherComponent';

// src/components/index.js
export * from './analyzer';
export * from './dashboard';
export * from './ui';
```

---

*This component documentation is maintained by the Privacy Protocol development team. For questions, improvements, or new component requests, please create an issue or submit a pull request.*
