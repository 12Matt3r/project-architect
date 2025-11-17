/**
 * Template #37: Inventory Demand Predictor - React Frontend
 * 
 * Advanced supply chain forecasting interface with time-series analysis and inventory optimization.
 * Displays demand predictions, inventory recommendations, and prioritized stocking actions.
 * 
 * Author: MiniMax Agent
 * Date: 2025-11-17
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  VStack,
  HStack,
  Text,
  Button,
  Input,
  Card,
  CardBody,
  CardHeader,
  Heading,
  Flex,
  Badge,
  Progress,
  Divider,
  Stack,
  StackDivider,
  useToast,
  Spinner,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  Wrap,
  WrapItem,
  Tooltip,
  IconButton,
  Select,
  NumberInput,
  NumberInputField,
  NumberInputStepper,
  NumberIncrementStepper,
  NumberDecrementStepper,
  FormControl,
  FormLabel,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
  SimpleGrid,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  StatArrow,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  Accordion,
  AccordionItem,
  AccordionButton,
  AccordionPanel,
  AccordionIcon,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalFooter,
  ModalBody,
  ModalCloseButton,
  useDisclosure,
  Grid,
  GridItem,
  AspectRatio,
  Link,
  Code
} from '@chakra-ui/react';
import {
  FiPackage,
  FiTrendingUp,
  FiTrendingDown,
  FiAlertTriangle,
  FiCheckCircle,
  FiClock,
  FiTarget,
  FiBarChart3,
  FiDollarSign,
  FiRefreshCw,
  FiDownload,
  FiShare2,
  FiInfo,
  FiLayers,
  FiActivity,
  FiCalendar,
  FiArrowUp,
  FiArrowDown,
  FiMinus,
  FiMaximize2
} from 'react-icons/fi';

// API Configuration
const API_BASE_URL = 'http://localhost:8000/api/v1';

// Types and Interfaces
interface SalesRecord {
  date: string;
  product_id: string;
  product_name: string;
  category: string;
  quantity_sold: number;
  revenue: number;
  price_per_unit: number;
  seasonality: string;
  trend_factor: number;
}

interface InventoryPrediction {
  product_id: string;
  product_name: string;
  current_stock: number;
  predicted_demand: number;
  recommended_stock: number;
  reorder_point: number;
  safety_stock: number;
  confidence_level: number;
  stockout_risk: string;
}

interface StockingAction {
  action_id: string;
  product_name: string;
  category: string;
  action_type: string;
  priority: string;
  quantity: number;
  reasoning: string;
  urgency_score: number;
  estimated_impact: string;
}

interface DemandForecast {
  product_category: string;
  forecast_period: string;
  predictions: InventoryPrediction[];
  stocking_actions: StockingAction[];
  summary: {
    total_products: number;
    total_predicted_demand: number;
    total_recommended_stock: number;
    average_confidence: number;
    risk_distribution: Record<string, number>;
    forecast_accuracy: string;
    next_review_date: string;
  };
  confidence_metrics: {
    model_accuracy: number;
    data_quality: number;
    forecast_reliability: number;
    seasonal_adjustment: number;
    lead_time_factor: number;
  };
  generated_at: string;
}

interface ProductCategory {
  description: string;
  products: string[];
  seasonality: string;
  growth_trend: string;
}

// Main Component
const InventoryDemandPredictor: React.FC = () => {
  // State Management
  const [selectedCategory, setSelectedCategory] = useState('');
  const [historicalPeriod, setHistoricalPeriod] = useState('12m');
  const [seasonalityFactor, setSeasonalityFactor] = useState(1.0);
  const [leadTimeDays, setLeadTimeDays] = useState(30);
  const [isForecasting, setIsForecasting] = useState(false);
  const [currentForecast, setCurrentForecast] = useState<DemandForecast | null>(null);
  const [salesData, setSalesData] = useState<SalesRecord[]>([]);
  const [forecastHistory, setForecastHistory] = useState<any[]>([]);
  const [productCategories, setProductCategories] = useState<Record<string, ProductCategory>>({});
  const [showAdvancedOptions, setShowAdvancedOptions] = useState(false);
  const [comparisonScenarios, setComparisonScenarios] = useState<string[]>([]);
  
  // Hooks
  const toast = useToast();
  const { isOpen, onOpen, onClose } = useDisclosure();
  const { isOpen: isHistoryOpen, onOpen: onHistoryOpen, onClose: onHistoryClose } = useDisclosure();

  // Load initial data
  useEffect(() => {
    loadProductCategories();
    loadForecastHistory();
  }, []);

  // API Functions
  const loadProductCategories = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/product-categories`);
      const data = await response.json();
      setProductCategories(data.categories || {});
    } catch (error) {
      console.error('Failed to load product categories:', error);
    }
  };

  const loadForecastHistory = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/forecast-history?limit=20`);
      const data = await response.json();
      setForecastHistory(data.history || []);
    } catch (error) {
      console.error('Failed to load forecast history:', error);
    }
  };

  const generateSalesData = async () => {
    if (!selectedCategory) {
      toast({
        title: 'Category Required',
        description: 'Please select a product category',
        status: 'warning',
        duration: 3000,
        isClosable: true
      });
      return;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/generate-sales-data`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          product_category: selectedCategory,
          historical_period: historicalPeriod,
          seasonality_factor: seasonalityFactor,
          lead_time_days: leadTimeDays
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to generate sales data');
      }

      const data = await response.json();
      setSalesData(data.sales_data || []);
      
      toast({
        title: 'Sales Data Generated',
        description: `Generated ${data.total_records} sales records`,
        status: 'success',
        duration: 3000,
        isClosable: true
      });

    } catch (error) {
      toast({
        title: 'Data Generation Error',
        description: 'Failed to generate sales data. Please try again.',
        status: 'error',
        duration: 5000,
        isClosable: true
      });
    }
  };

  const forecastDemand = async () => {
    if (!selectedCategory) {
      toast({
        title: 'Category Required',
        description: 'Please select a product category',
        status: 'warning',
        duration: 3000,
        isClosable: true
      });
      return;
    }

    setIsForecasting(true);

    try {
      const response = await fetch(`${API_BASE_URL}/forecast-demand`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          product_category: selectedCategory,
          historical_period: historicalPeriod,
          seasonality_factor: seasonalityFactor,
          lead_time_days: leadTimeDays
        }),
      });

      if (!response.ok) {
        throw new Error('Forecast failed');
      }

      const data: DemandForecast = await response.json();
      setCurrentForecast(data);
      loadForecastHistory();

      toast({
        title: 'Forecast Complete',
        description: 'Demand forecast and stocking recommendations generated',
        status: 'success',
        duration: 3000,
        isClosable: true
      });

    } catch (error) {
      toast({
        title: 'Forecast Error',
        description: 'Failed to generate demand forecast. Please try again.',
        status: 'error',
        duration: 5000,
        isClosable: true
      });
    } finally {
      setIsForecasting(false);
    }
  };

  // Utility Functions
  const getRiskColor = (risk: string) => {
    switch (risk.toLowerCase()) {
      case 'low': return 'green';
      case 'medium': return 'yellow';
      case 'high': return 'orange';
      case 'very high': return 'red';
      default: return 'gray';
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority.toLowerCase()) {
      case 'high': return 'red';
      case 'medium': return 'yellow';
      case 'low': return 'blue';
      default: return 'gray';
    }
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(value);
  };

  const formatNumber = (value: number) => {
    return new Intl.NumberFormat('en-US').format(value);
  };

  // Component: Sales Data Overview
  const SalesDataOverview: React.FC<{ data: SalesRecord[] }> = ({ data }) => {
    if (data.length === 0) return null;

    const totalRevenue = data.reduce((sum, record) => sum + record.revenue, 0);
    const totalQuantity = data.reduce((sum, record) => sum + record.quantity_sold, 0);
    const uniqueProducts = [...new Set(data.map(record => record.product_name))].length;
    const dateRange = {
      start: Math.min(...data.map(record => new Date(record.date).getTime())),
      end: Math.max(...data.map(record => new Date(record.date).getTime()))
    };

    return (
      <Card>
        <CardHeader>
          <Heading size="md">Sales Data Overview</Heading>
        </CardHeader>
        <CardBody pt={0}>
          <SimpleGrid columns={{ base: 1, md: 4 }} spacing={4}>
            <Stat>
              <StatLabel>Total Revenue</StatLabel>
              <StatNumber color="green.500">{formatCurrency(totalRevenue)}</StatNumber>
              <StatHelpText>Historical period</StatHelpText>
            </Stat>
            
            <Stat>
              <StatLabel>Total Units Sold</StatLabel>
              <StatNumber>{formatNumber(totalQuantity)}</StatNumber>
              <StatHelpText>Across all products</StatHelpText>
            </Stat>
            
            <Stat>
              <StatLabel>Unique Products</StatLabel>
              <StatNumber>{uniqueProducts}</StatNumber>
              <StatHelpText>In category</StatHelpText>
            </Stat>
            
            <Stat>
              <StatLabel>Data Period</StatLabel>
              <StatNumber fontSize="md">
                {Math.ceil((dateRange.end - dateRange.start) / (1000 * 60 * 60 * 24 * 30))} months
              </StatNumber>
              <StatHelpText>
                {new Date(dateRange.start).toLocaleDateString()} - {new Date(dateRange.end).toLocaleDateString()}
              </StatHelpText>
            </Stat>
          </SimpleGrid>
        </CardBody>
      </Card>
    );
  };

  // Component: Inventory Prediction Card
  const InventoryPredictionCard: React.FC<{ prediction: InventoryPrediction }> = ({ prediction }) => {
    const stockStatus = prediction.current_stock >= prediction.recommended_stock ? 'Sufficient' : 'Low';
    const stockColor = stockStatus === 'Sufficient' ? 'green' : 'red';

    return (
      <Card borderWidth={1} borderColor="gray.200">
        <CardBody>
          <VStack spacing={4} align="stretch">
            
            {/* Header */}
            <HStack justify="space-between">
              <VStack align="start" spacing={1}>
                <Text fontWeight="bold" fontSize="lg">{prediction.product_name}</Text>
                <Text fontSize="sm" color="gray.600">ID: {prediction.product_id}</Text>
              </VStack>
              <VStack align="end" spacing={1}>
                <Badge 
                  colorScheme={getRiskColor(prediction.stockout_risk)} 
                  variant="solid"
                  fontSize="sm"
                >
                  {prediction.stockout_risk} Risk
                </Badge>
                <Text fontSize="xs" color="gray.500">
                  {prediction.confidence_level.toFixed(1)}% confidence
                </Text>
              </VStack>
            </HStack>

            {/* Stock Levels */}
            <SimpleGrid columns={2} spacing={4}>
              <Box>
                <Text fontSize="sm" color="gray.600">Current Stock</Text>
                <Text fontWeight="bold" fontSize="lg">{formatNumber(prediction.current_stock)}</Text>
              </Box>
              <Box>
                <Text fontSize="sm" color="gray.600">Predicted Demand</Text>
                <Text fontWeight="bold" fontSize="lg">{formatNumber(prediction.predicted_demand)}</Text>
              </Box>
              <Box>
                <Text fontSize="sm" color="gray.600">Recommended Stock</Text>
                <Text fontWeight="bold" color="blue.600">{formatNumber(prediction.recommended_stock)}</Text>
              </Box>
              <Box>
                <Text fontSize="sm" color="gray.600">Reorder Point</Text>
                <Text fontWeight="bold" color="orange.600">{formatNumber(prediction.reorder_point)}</Text>
              </Box>
            </SimpleGrid>

            {/* Stock Status */}
            <Box>
              <HStack justify="space-between" mb={2}>
                <Text fontSize="sm" fontWeight="semibold">Stock Status</Text>
                <Badge colorScheme={stockColor} variant="outline">{stockStatus}</Badge>
              </HStack>
              <Progress 
                value={Math.min(100, (prediction.current_stock / prediction.recommended_stock) * 100)} 
                colorScheme={stockColor}
                size="sm"
                borderRadius="md"
              />
            </Box>

            {/* Safety Stock */}
            <HStack justify="space-between">
              <Text fontSize="sm" color="gray.600">Safety Stock</Text>
              <Text fontSize="sm" fontWeight="bold">{formatNumber(prediction.safety_stock)}</Text>
            </HStack>

            {/* Stock Level Comparison */}
            <Box p={3} bg="gray.50" borderRadius="md">
              <VStack spacing={2}>
                <HStack justify="space-between" w="full">
                  <Text fontSize="sm">Current</Text>
                  <Text fontSize="sm" fontWeight="bold">{prediction.current_stock}</Text>
                </HStack>
                <HStack justify="space-between" w="full">
                  <Text fontSize="sm">Recommended</Text>
                  <Text fontSize="sm" fontWeight="bold">{prediction.recommended_stock}</Text>
                </HStack>
                <HStack justify="space-between" w="full">
                  <Text fontSize="sm">Gap</Text>
                  <Text fontSize="sm" fontWeight="bold" color={prediction.recommended_stock - prediction.current_stock > 0 ? 'red.500' : 'green.500'}>
                    {prediction.recommended_stock - prediction.current_stock > 0 ? '+' : ''}{prediction.recommended_stock - prediction.current_stock}
                  </Text>
                </HStack>
              </VStack>
            </Box>
          </VStack>
        </CardBody>
      </Card>
    );
  };

  // Component: Stocking Action Card
  const StockingActionCard: React.FC<{ action: StockingAction }> = ({ action }) => {
    return (
      <Card 
        borderWidth={2} 
        borderColor={`${getPriorityColor(action.priority)}.200`}
        bg={`${getPriorityColor(action.priority)}.50`}
      >
        <CardBody>
          <VStack spacing={3} align="stretch">
            
            {/* Action Header */}
            <HStack justify="space-between">
              <VStack align="start" spacing={1}>
                <HStack>
                  <Text fontWeight="bold">{action.action_type}</Text>
                  <Badge 
                    colorScheme={getPriorityColor(action.priority)} 
                    variant="solid"
                  >
                    {action.priority}
                  </Badge>
                </HStack>
                <Text fontSize="sm" color="gray.600">{action.product_name}</Text>
              </VStack>
              <VStack align="end" spacing={1}>
                <Text fontSize="lg" fontWeight="bold" color={`${getPriorityColor(action.priority)}.700`}>
                  {action.urgency_score.toFixed(1)}
                </Text>
                <Text fontSize="xs" color="gray.500">Urgency</Text>
              </VStack>
            </HStack>

            {/* Quantity and Category */}
            <HStack justify="space-between">
              <HStack>
                <FiPackage size={16} />
                <Text fontSize="sm">Quantity: {formatNumber(action.quantity)}</Text>
              </HStack>
              <Badge variant="outline">{action.category}</Badge>
            </HStack>

            {/* Reasoning */}
            <Box>
              <Text fontSize="sm" fontWeight="semibold" mb={1}>Reasoning</Text>
              <Text fontSize="sm" color="gray.700">{action.reasoning}</Text>
            </Box>

            {/* Impact */}
            <Alert status={getPriorityColor(action.priority) === 'red' ? 'error' : 
                          getPriorityColor(action.priority) === 'yellow' ? 'warning' : 'info'}>
              <AlertIcon />
              <Box>
                <Text fontSize="sm" fontWeight="semibold">Estimated Impact</Text>
                <Text fontSize="sm">{action.estimated_impact}</Text>
              </Box>
            </Alert>
          </VStack>
        </CardBody>
      </Card>
    );
  };

  return (
    <Box minH="100vh" bg="gray.50" p={4}>
      <VStack spacing={6} align="stretch" maxW="7xl" mx="auto">
        
        {/* Header */}
        <Card>
          <CardBody>
            <VStack spacing={4}>
              <HStack justify="space-between" w="full">
                <VStack align="start" spacing={1}>
                  <Heading size="lg">Inventory Demand Predictor</Heading>
                  <Text color="gray.600">
                    Advanced supply chain forecasting with time-series analysis and inventory optimization
                  </Text>
                </VStack>
                <HStack>
                  <Button
                    leftIcon={<FiHistory />}
                    variant="ghost"
                    size="sm"
                    onClick={onHistoryOpen}
                  >
                    Forecast History
                  </Button>
                  <Button
                    leftIcon={<FiInfo />}
                    variant="outline"
                    size="sm"
                    onClick={onOpen}
                  >
                    Documentation
                  </Button>
                </HStack>
              </HStack>

              <HStack spacing={4} w="full">
                <Select
                  placeholder="Select product category"
                  value={selectedCategory}
                  onChange={(e) => setSelectedCategory(e.target.value)}
                  size="lg"
                  flex={2}
                >
                  {Object.entries(productCategories).map(([category, info]) => (
                    <option key={category} value={category}>
                      {category} - {info.description}
                    </option>
                  ))}
                </Select>
                
                <Select
                  value={historicalPeriod}
                  onChange={(e) => setHistoricalPeriod(e.target.value)}
                  size="lg"
                  flex={1}
                >
                  <option value="6m">6 Months</option>
                  <option value="12m">12 Months</option>
                  <option value="24m">24 Months</option>
                </Select>
                
                <Button
                  leftIcon={isForecasting ? <Spinner size="sm" /> : <FiBarChart3 />}
                  colorScheme="blue"
                  size="lg"
                  onClick={forecastDemand}
                  isLoading={isForecasting}
                  loadingText="Forecasting..."
                >
                  Forecast Demand
                </Button>
              </HStack>
            </VStack>
          </CardBody>
        </Card>

        {/* Advanced Options */}
        <Card>
          <CardHeader>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setShowAdvancedOptions(!showAdvancedOptions)}
              leftIcon={showAdvancedOptions ? <FiMinus /> : <FiPlus />}
            >
              Advanced Options
            </Button>
          </CardHeader>
          {showAdvancedOptions && (
            <CardBody pt={0}>
              <SimpleGrid columns={{ base: 1, md: 3 }} spacing={4}>
                <FormControl>
                  <FormLabel fontSize="sm">Seasonality Factor</FormLabel>
                  <NumberInput
                    value={seasonalityFactor}
                    onChange={(valueString) => setSeasonalityFactor(parseFloat(valueString) || 1.0)}
                    min={0.5}
                    max={2.0}
                    step={0.1}
                    precision={2}
                  >
                    <NumberInputField />
                    <NumberInputStepper>
                      <NumberIncrementStepper />
                      <NumberDecrementStepper />
                    </NumberInputStepper>
                  </NumberInput>
                  <Text fontSize="xs" color="gray.500" mt={1}>
                    Adjust for seasonal variations
                  </Text>
                </FormControl>
                
                <FormControl>
                  <FormLabel fontSize="sm">Lead Time (Days)</FormLabel>
                  <NumberInput
                    value={leadTimeDays}
                    onChange={(valueString) => setLeadTimeDays(parseInt(valueString) || 30)}
                    min={7}
                    max={90}
                    step={5}
                  >
                    <NumberInputField />
                    <NumberInputStepper>
                      <NumberIncrementStepper />
                      <NumberDecrementStepper />
                    </NumberInputStepper>
                  </NumberInput>
                  <Text fontSize="xs" color="gray.500" mt={1}>
                    Supplier lead time for orders
                  </Text>
                </FormControl>
                
                <FormControl>
                  <FormLabel fontSize="sm">Actions</FormLabel>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={generateSalesData}
                    leftIcon={<FiRefreshCw />}
                    w="full"
                  >
                    Generate Sample Data
                  </Button>
                </FormControl>
              </SimpleGrid>
            </CardBody>
          )}
        </Card>

        {/* Main Content */}
        <Grid templateColumns={{ base: '1fr', lg: '2fr 1fr' }} gap={6}>
          
          {/* Left Column: Analysis Results */}
          <VStack spacing={6} align="stretch">
            
            {/* Sales Data Overview */}
            {salesData.length > 0 && (
              <SalesDataOverview data={salesData} />
            )}

            {/* Current Forecast */}
            {currentForecast && (
              <VStack spacing={6} align="stretch">
                
                {/* Forecast Summary */}
                <Card>
                  <CardHeader>
                    <HStack justify="space-between">
                      <VStack align="start" spacing={1}>
                        <Heading size="md">Forecast Summary</Heading>
                        <Text fontSize="sm" color="gray.600">
                          {currentForecast.product_category} - {currentForecast.forecast_period}
                        </Text>
                      </VStack>
                      <Badge colorScheme="green" variant="solid">
                        Generated: {new Date(currentForecast.generated_at).toLocaleString()}
                      </Badge>
                    </HStack>
                  </CardHeader>
                  <CardBody pt={0}>
                    <SimpleGrid columns={{ base: 2, md: 4 }} spacing={4}>
                      <Stat>
                        <StatLabel>Total Products</StatLabel>
                        <StatNumber>{currentForecast.summary.total_products}</StatNumber>
                      </Stat>
                      <Stat>
                        <StatLabel>Predicted Demand</StatLabel>
                        <StatNumber>{formatNumber(currentForecast.summary.total_predicted_demand)}</StatNumber>
                        <StatHelpText>Next quarter</StatHelpText>
                      </Stat>
                      <Stat>
                        <StatLabel>Recommended Stock</StatLabel>
                        <StatNumber color="blue.600">{formatNumber(currentForecast.summary.total_recommended_stock)}</StatNumber>
                        <StatHelpText>Optimal level</StatHelpText>
                      </Stat>
                      <Stat>
                        <StatLabel>Avg Confidence</StatLabel>
                        <StatNumber>{currentForecast.summary.average_confidence.toFixed(1)}%</StatNumber>
                        <StatHelpText>Forecast accuracy</StatHelpText>
                      </Stat>
                    </SimpleGrid>
                  </CardBody>
                </Card>

                {/* Risk Distribution */}
                <Card>
                  <CardHeader>
                    <Heading size="md">Risk Distribution</Heading>
                  </CardHeader>
                  <CardBody pt={0}>
                    <HStack spacing={4}>
                      {Object.entries(currentForecast.summary.risk_distribution).map(([risk, count]) => (
                        <VStack key={risk} spacing={1}>
                          <Text fontSize="2xl" fontWeight="bold" color={`${getRiskColor(risk)}.500`}>
                            {count}
                          </Text>
                          <Badge colorScheme={getRiskColor(risk)} variant="subtle">
                            {risk}
                          </Badge>
                        </VStack>
                      ))}
                    </HStack>
                  </CardBody>
                </Card>

                {/* Inventory Predictions */}
                <Card>
                  <CardHeader>
                    <Heading size="md">Inventory Predictions</Heading>
                  </CardHeader>
                  <CardBody pt={0}>
                    <VStack spacing={4} align="stretch">
                      {currentForecast.predictions.map((prediction, index) => (
                        <InventoryPredictionCard key={prediction.product_id} prediction={prediction} />
                      ))}
                    </VStack>
                  </CardBody>
                </Card>

                {/* Stocking Actions */}
                <Card>
                  <CardHeader>
                    <HStack justify="space-between">
                      <Heading size="md">Prioritized Stocking Actions</Heading>
                      <Text fontSize="sm" color="gray.600">
                        {currentForecast.stocking_actions.length} actions recommended
                      </Text>
                    </HStack>
                  </CardHeader>
                  <CardBody pt={0}>
                    <VStack spacing={4} align="stretch">
                      {currentForecast.stocking_actions.map((action, index) => (
                        <StockingActionCard key={action.action_id} action={action} />
                      ))}
                    </VStack>
                  </CardBody>
                </Card>
              </VStack>
            )}

            {/* Processing Indicator */}
            {isForecasting && (
              <Card>
                <CardBody>
                  <VStack spacing={4}>
                    <Spinner size="xl" color="blue.500" />
                    <Text fontWeight="semibold">Analyzing demand patterns...</Text>
                    <Text fontSize="sm" color="gray.600" textAlign="center">
                      Processing historical data, building time-series models, and generating predictions
                    </Text>
                    <Progress 
                      size="sm" 
                      isIndeterminate 
                      colorScheme="blue" 
                      w="full" 
                      borderRadius="md"
                    />
                  </VStack>
                </CardBody>
              </Card>
            )}
          </VStack>

          {/* Right Column: Sidebar */}
          <VStack spacing={6} align="stretch">
            
            {/* Category Information */}
            {selectedCategory && productCategories[selectedCategory] && (
              <Card>
                <CardHeader>
                  <Heading size="sm">{selectedCategory}</Heading>
                </CardHeader>
                <CardBody pt={0}>
                  <VStack spacing={3} align="stretch">
                    <Text fontSize="sm">{productCategories[selectedCategory].description}</Text>
                    
                    <Box>
                      <Text fontSize="sm" fontWeight="semibold" mb={2}>Products</Text>
                      <Wrap>
                        {productCategories[selectedCategory].products.map((product, index) => (
                          <WrapItem key={index}>
                            <Badge variant="outline" fontSize="xs">{product}</Badge>
                          </WrapItem>
                        ))}
                      </Wrap>
                    </Box>
                    
                    <HStack justify="space-between">
                      <Text fontSize="sm" color="gray.600">Seasonality</Text>
                      <Badge colorScheme="purple" variant="subtle">
                        {productCategories[selectedCategory].seasonality}
                      </Badge>
                    </HStack>
                    
                    <HStack justify="space-between">
                      <Text fontSize="sm" color="gray.600">Growth Trend</Text>
                      <Badge colorScheme="green" variant="subtle">
                        {productCategories[selectedCategory].growth_trend}
                      </Badge>
                    </HStack>
                  </VStack>
                </CardBody>
              </Card>
            )}

            {/* Forecast Methodology */}
            <Card>
              <CardHeader>
                <Heading size="sm">Forecasting Methodology</Heading>
              </CardHeader>
              <CardBody pt={0}>
                <VStack spacing={3} align="stretch">
                  <Text fontSize="sm">
                    Our forecasting engine uses advanced time-series analysis to predict inventory needs:
                  </Text>
                  
                  <VStack spacing={2} align="stretch">
                    <HStack>
                      <Box w={3} h={3} bg="blue.400" borderRadius="full" />
                      <Text fontSize="sm"><strong>Trend Analysis:</strong> Linear regression on historical patterns</Text>
                    </HStack>
                    <HStack>
                      <Box w={3} h={3} bg="green.400" borderRadius="full" />
                      <Text fontSize="sm"><strong>Seasonal Adjustment:</strong> Monthly seasonal coefficients</Text>
                    </HStack>
                    <HStack>
                      <Box w={3} h={3} bg="purple.400" borderRadius="full" />
                      <Text fontSize="sm"><strong>Safety Stock:</strong> Service level-based calculations</Text>
                    </HStack>
                    <HStack>
                      <Box w={3} h={3} bg="orange.400" borderRadius="full" />
                      <Text fontSize="sm"><strong>Risk Assessment:</strong> Stockout probability analysis</Text>
                    </HStack>
                  </VStack>
                </VStack>
              </CardBody>
            </Card>

            {/* Confidence Metrics */}
            {currentForecast && (
              <Card>
                <CardHeader>
                  <Heading size="sm">Confidence Metrics</Heading>
                </CardHeader>
                <CardBody pt={0}>
                  <VStack spacing={3} align="stretch">
                    <Box>
                      <HStack justify="space-between" mb={1}>
                        <Text fontSize="sm">Model Accuracy</Text>
                        <Text fontSize="sm" fontWeight="bold">
                          {currentForecast.confidence_metrics.model_accuracy.toFixed(1)}%
                        </Text>
                      </HStack>
                      <Progress 
                        value={currentForecast.confidence_metrics.model_accuracy} 
                        colorScheme="green" 
                        size="sm"
                        borderRadius="md"
                      />
                    </Box>
                    
                    <Box>
                      <HStack justify="space-between" mb={1}>
                        <Text fontSize="sm">Data Quality</Text>
                        <Text fontSize="sm" fontWeight="bold">
                          {currentForecast.confidence_metrics.data_quality.toFixed(1)}%
                        </Text>
                      </HStack>
                      <Progress 
                        value={currentForecast.confidence_metrics.data_quality} 
                        colorScheme="blue" 
                        size="sm"
                        borderRadius="md"
                      />
                    </Box>
                    
                    <Box>
                      <HStack justify="space-between" mb={1}>
                        <Text fontSize="sm">Forecast Reliability</Text>
                        <Text fontSize="sm" fontWeight="bold">
                          {currentForecast.confidence_metrics.forecast_reliability.toFixed(1)}%
                        </Text>
                      </HStack>
                      <Progress 
                        value={currentForecast.confidence_metrics.forecast_reliability} 
                        colorScheme="purple" 
                        size="sm"
                        borderRadius="md"
                      />
                    </Box>
                  </VStack>
                </CardBody>
              </Card>
            )}

            {/* Quick Actions */}
            <Card>
              <CardHeader>
                <Heading size="sm">Quick Actions</Heading>
              </CardHeader>
              <CardBody pt={0}>
                <VStack spacing={3} align="stretch">
                  <Button size="sm" variant="outline" leftIcon={<FiRefreshCw />}>
                    Refresh Forecast
                  </Button>
                  <Button size="sm" variant="outline" leftIcon={<FiDownload />}>
                    Export Results
                  </Button>
                  <Button size="sm" variant="outline" leftIcon={<FiShare2 />}>
                    Share Analysis
                  </Button>
                  <Button size="sm" variant="outline" leftIcon={<FiCalendar />}>
                    Schedule Review
                  </Button>
                </VStack>
              </CardBody>
            </Card>
          </VStack>
        </Grid>
      </VStack>

      {/* Documentation Modal */}
      <Modal isOpen={isOpen} onClose={onClose} size="4xl">
        <ModalOverlay />
        <ModalContent maxH="90vh" overflowY="auto">
          <ModalHeader>Inventory Demand Predictor Documentation</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <VStack spacing={6} align="stretch">
              
              <Box>
                <Heading size="md" mb={3}>Forecasting Methodology</Heading>
                <VStack spacing={4} align="stretch">
                  <Box>
                    <Text fontWeight="semibold" color="blue.600">Time-Series Analysis</Text>
                    <Text fontSize="sm">
                      Our forecasting engine analyzes historical sales data to identify trends, seasonality, and patterns
                      that inform future demand predictions. The system uses multiple statistical models to ensure accuracy.
                    </Text>
                  </Box>
                  <Box>
                    <Text fontWeight="semibold" color="green.600">Inventory Optimization</Text>
                    <Text fontSize="sm">
                      Based on demand forecasts, we calculate optimal inventory levels including safety stock,
                      reorder points, and recommended stock quantities to minimize stockout risk while controlling costs.
                    </Text>
                  </Box>
                  <Box>
                    <Text fontWeight="semibold" color="purple.600">Risk Assessment</Text>
                    <Text fontSize="sm">
                      Each prediction includes a risk assessment indicating the likelihood of stockouts,
                      helping prioritize stocking actions based on urgency and impact.
                    </Text>
                  </Box>
                </VStack>
              </Box>

              <Divider />

              <Box>
                <Heading size="md" mb={3}>Key Metrics Explained</Heading>
                <VStack spacing={3} align="stretch">
                  <HStack>
                    <Badge colorScheme="blue">Predicted Demand</Badge>
                    <Text fontSize="sm">Expected units to be sold in the next quarter</Text>
                  </HStack>
                  <HStack>
                    <Badge colorScheme="green">Recommended Stock</Badge>
                    <Text fontSize="sm">Optimal inventory level including safety stock</Text>
                  </HStack>
                  <HStack>
                    <Badge colorScheme="orange">Reorder Point</Badge>
                    <Text fontSize="sm">Stock level that triggers a new purchase order</Text>
                  </HStack>
                  <HStack>
                    <Badge colorScheme="purple">Safety Stock</Badge>
                    <Text fontSize="sm">Buffer inventory to prevent stockouts during demand spikes</Text>
                  </HStack>
                </VStack>
              </Box>

              <Divider />

              <Box>
                <Heading size="md" mb={3}>Action Priorities</Heading>
                <VStack spacing={3} align="stretch">
                  <HStack>
                    <Badge colorScheme="red">High Priority</Badge>
                    <Text fontSize="sm">Immediate action required - high stockout risk</Text>
                  </HStack>
                  <HStack>
                    <Badge colorScheme="yellow">Medium Priority</Badge>
                    <Text fontSize="sm">Action recommended within 1-2 weeks</Text>
                  </HStack>
                  <HStack>
                    <Badge colorScheme="blue">Low Priority</Badge>
                    <Text fontSize="sm">Optimization opportunities for future consideration</Text>
                  </HStack>
                </VStack>
              </Box>

              <Divider />

              <Alert status="info">
                <AlertIcon />
                <Box>
                  <Text fontSize="sm">
                    <strong>Note:</strong> All data in this demonstration is simulated for educational purposes. 
                    In production, the system would integrate with real inventory management systems,
                    POS data, and supplier information for accurate forecasting.
                  </Text>
                </Box>
              </Alert>
            </VStack>
          </ModalBody>
          <ModalFooter>
            <Button onClick={onClose}>Close</Button>
          </ModalFooter>
        </ModalContent>
      </Modal>

      {/* Forecast History Modal */}
      <Modal isOpen={isHistoryOpen} onClose={onHistoryClose} size="xl">
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>Forecast History</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <VStack spacing={3} align="stretch">
              {forecastHistory.length === 0 ? (
                <Text color="gray.500" textAlign="center" py={8}>
                  No forecast history available
                </Text>
              ) : (
                forecastHistory.map((forecast, index) => (
                  <Card key={index} size="sm" variant="outline">
                    <CardBody>
                      <HStack justify="space-between">
                        <VStack align="start" spacing={1}>
                          <Text fontSize="sm" fontWeight="semibold">
                            {forecast.category} - {forecast.forecast_period}
                          </Text>
                          <Text fontSize="xs" color="gray.500">
                            Forecast ID: {forecast.forecast_id.substring(0, 8)}...
                          </Text>
                        </VStack>
                        <Text fontSize="xs" color="gray.500">
                          {new Date(forecast.timestamp).toLocaleString()}
                        </Text>
                      </HStack>
                    </CardBody>
                  </Card>
                ))
              )}
            </VStack>
          </ModalBody>
          <ModalFooter>
            <Button variant="ghost" onClick={onHistoryClose}>
              Close
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </Box>
  );
};

export default InventoryDemandPredictor;