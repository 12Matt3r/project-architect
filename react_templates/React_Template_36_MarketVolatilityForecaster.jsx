/**
 * Template #36: Market Volatility Forecaster - React Frontend
 * 
 * Advanced financial risk analysis interface with comprehensive metrics visualization.
 * Displays Sharpe Ratio, Sortino Ratio, Maximum Drawdown with narrative assessments.
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
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
  Grid,
  GridItem,
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
  Select,
  NumberInput,
  NumberInputField,
  NumberInputStepper,
  NumberIncrementStepper,
  NumberDecrementStepper,
  FormControl,
  FormLabel,
  Textarea,
  Link
} from '@chakra-ui/react';
import {
  FiTrendingUp,
  FiTrendingDown,
  FiActivity,
  FiShield,
  FiBarChart3,
  FiDollarSign,
  FiAlertTriangle,
  FiCheckCircle,
  FiInfo,
  FiRefreshCw,
  FiDownload,
  FiShare2,
  FiExternalLink,
  FiClock,
  FiTarget,
  FiTrendingDown as FiMaxDrawdown
} from 'react-icons/fi';

// API Configuration
const API_BASE_URL = 'http://localhost:8000/api/v1';

// Types and Interfaces
interface RiskMetrics {
  sharpe_ratio: number;
  sortino_ratio: number;
  max_drawdown: number;
  annualized_return: number;
  annualized_volatility: number;
  best_day_return: number;
  worst_day_return: number;
  total_return: number;
}

interface RiskAssessment {
  risk_level: string;
  risk_factors: string[];
  volatility_assessment: string;
  return_assessment: string;
  drawdown_assessment: string;
  overall_narrative: string;
  investment_recommendation: string;
}

interface MarketContext {
  data_source: string;
  analysis_period: string;
  trading_days_analyzed: number;
  price_range: {
    min: number;
    max: number;
    current: number;
  };
  return_distribution: {
    mean: number;
    std: number;
    skewness: number;
    kurtosis: number;
  };
}

interface AnalysisResponse {
  ticker: string;
  analysis_period: string;
  risk_metrics: RiskMetrics;
  risk_assessment: RiskAssessment;
  market_context: MarketContext;
  confidence_level: number;
  analysis_timestamp: string;
}

interface TickerComparison {
  ticker: string;
  sharpe_ratio: number;
  sortino_ratio: number;
  max_drawdown: number;
  annualized_return: number;
  annualized_volatility: number;
  risk_level: string;
  data_source: string;
}

// Main Component
const MarketVolatilityForecaster: React.FC = () => {
  // State Management
  const [ticker, setTicker] = useState('');
  const [analysisPeriod, setAnalysisPeriod] = useState('3y');
  const [riskFreeRate, setRiskFreeRate] = useState(0.02);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [currentAnalysis, setCurrentAnalysis] = useState<AnalysisResponse | null>(null);
  const [analysisHistory, setAnalysisHistory] = useState<any[]>([]);
  const [supportedTickers, setSupportedTickers] = useState<any>({});
  const [marketIndicators, setMarketIndicators] = useState<any>(null);
  const [comparisonTickers, setComparisonTickers] = useState('');
  const [comparisonResults, setComparisonResults] = useState<TickerComparison[]>([]);
  const [isComparing, setIsComparing] = useState(false);
  
  // Hooks
  const toast = useToast();
  const { isOpen, onOpen, onClose } = useDisclosure();

  // Load initial data
  useEffect(() => {
    loadSupportedTickers();
    loadMarketIndicators();
    loadAnalysisHistory();
  }, []);

  // API Functions
  const loadSupportedTickers = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/supported-tickers`);
      const data = await response.json();
      setSupportedTickers(data.supported_tickers || {});
    } catch (error) {
      console.error('Failed to load supported tickers:', error);
    }
  };

  const loadMarketIndicators = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/market-indicators`);
      const data = await response.json();
      setMarketIndicators(data.indicators || null);
    } catch (error) {
      console.error('Failed to load market indicators:', error);
    }
  };

  const loadAnalysisHistory = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/analysis-history?limit=20`);
      const data = await response.json();
      setAnalysisHistory(data.history || []);
    } catch (error) {
      console.error('Failed to load analysis history:', error);
    }
  };

  const analyzeTicker = async () => {
    if (!ticker.trim()) {
      toast({
        title: 'Ticker Required',
        description: 'Please enter a stock ticker symbol',
        status: 'warning',
        duration: 3000,
        isClosable: true
      });
      return;
    }

    setIsAnalyzing(true);

    try {
      const response = await fetch(`${API_BASE_URL}/analyze-ticker`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ticker: ticker.toUpperCase(),
          period: analysisPeriod,
          risk_free_rate: riskFreeRate
        }),
      });

      if (!response.ok) {
        throw new Error('Analysis failed');
      }

      const data: AnalysisResponse = await response.json();
      setCurrentAnalysis(data);
      loadAnalysisHistory(); // Refresh history

      toast({
        title: 'Analysis Complete',
        description: `Risk analysis for ${data.ticker} completed successfully`,
        status: 'success',
        duration: 3000,
        isClosable: true
      });

    } catch (error) {
      toast({
        title: 'Analysis Error',
        description: 'Failed to analyze ticker. Please try again.',
        status: 'error',
        duration: 5000,
        isClosable: true
      });
    } finally {
      setIsAnalyzing(false);
    }
  };

  const compareTickers = async () => {
    if (!comparisonTickers.trim()) {
      toast({
        title: 'Tickers Required',
        description: 'Please enter ticker symbols to compare',
        status: 'warning',
        duration: 3000,
        isClosable: true
      });
      return;
    }

    setIsComparing(true);

    try {
      const response = await fetch(
        `${API_BASE_URL}/compare-tickers?tickers=${comparisonTickers}&period=${analysisPeriod}&risk_free_rate=${riskFreeRate}`
      );

      if (!response.ok) {
        throw new Error('Comparison failed');
      }

      const data = await response.json();
      setComparisonResults(data.comparisons || []);

      toast({
        title: 'Comparison Complete',
        description: 'Ticker comparison analysis completed',
        status: 'success',
        duration: 3000,
        isClosable: true
      });

    } catch (error) {
      toast({
        title: 'Comparison Error',
        description: 'Failed to compare tickers. Please try again.',
        status: 'error',
        duration: 5000,
        isClosable: true
      });
    } finally {
      setIsComparing(false);
    }
  };

  // Utility Functions
  const getRiskColor = (riskLevel: string) => {
    switch (riskLevel.toLowerCase()) {
      case 'low': return 'green';
      case 'moderate': return 'yellow';
      case 'high': return 'orange';
      case 'very high': return 'red';
      default: return 'gray';
    }
  };

  const formatPercentage = (value: number) => {
    return `${(value * 100).toFixed(2)}%`;
  };

  const formatRatio = (value: number) => {
    if (!isFinite(value)) return '∞';
    return value.toFixed(2);
  };

  const getMetricStatus = (value: number, thresholds: {good: number, fair: number}) => {
    if (value >= thresholds.good) return 'good';
    if (value >= thresholds.fair) return 'fair';
    return 'poor';
  };

  // Component: Risk Metrics Card
  const RiskMetricsCard: React.FC<{ metrics: RiskMetrics }> = ({ metrics }) => {
    return (
      <Card>
        <CardHeader>
          <HStack justify="space-between">
            <Heading size="md">Risk Metrics</Heading>
            <Badge colorScheme="blue" variant="subtle">
              3-Year Analysis
            </Badge>
          </HStack>
        </CardHeader>
        <CardBody pt={0}>
          <SimpleGrid columns={{ base: 1, md: 2 }} spacing={6}>
            
            {/* Sharpe Ratio */}
            <Stat>
              <StatLabel>
                <HStack>
                  <FiTrendingUp />
                  <Text>Sharpe Ratio</Text>
                  <Tooltip label="Risk-adjusted return metric">
                    <FiInfo />
                  </Tooltip>
                </HStack>
              </StatLabel>
              <StatNumber color={
                getMetricStatus(metrics.sharpe_ratio, {good: 1.0, fair: 0.5}) === 'good' ? 'green.500' :
                getMetricStatus(metrics.sharpe_ratio, {good: 1.0, fair: 0.5}) === 'fair' ? 'yellow.500' : 'red.500'
              }>
                {formatRatio(metrics.sharpe_ratio)}
              </StatNumber>
              <StatHelpText>
                {metrics.sharpe_ratio >= 1.0 ? 'Excellent' : 
                 metrics.sharpe_ratio >= 0.5 ? 'Good' : 'Poor'} risk-adjusted returns
              </StatHelpText>
            </Stat>

            {/* Sortino Ratio */}
            <Stat>
              <StatLabel>
                <HStack>
                  <FiShield />
                  <Text>Sortino Ratio</Text>
                  <Tooltip label="Downside risk-adjusted return metric">
                    <FiInfo />
                  </Tooltip>
                </HStack>
              </StatLabel>
              <StatNumber color={
                getMetricStatus(metrics.sortino_ratio, {good: 1.5, fair: 1.0}) === 'good' ? 'green.500' :
                getMetricStatus(metrics.sortino_ratio, {good: 1.5, fair: 1.0}) === 'fair' ? 'yellow.500' : 'red.500'
              }>
                {formatRatio(metrics.sortino_ratio)}
              </StatNumber>
              <StatHelpText>
                Focuses on downside risk
              </StatHelpText>
            </Stat>

            {/* Maximum Drawdown */}
            <Stat>
              <StatLabel>
                <HStack>
                  <FiMaxDrawdown />
                  <Text>Max Drawdown</Text>
                  <Tooltip label="Largest peak-to-trough decline">
                    <FiInfo />
                  </Tooltip>
                </HStack>
              </StatLabel>
              <StatNumber color="red.500">
                {formatPercentage(metrics.max_drawdown)}
              </StatNumber>
              <StatHelpText>
                {abs(metrics.max_drawdown) <= 0.15 ? 'Low' : 
                 abs(metrics.max_drawdown) <= 0.25 ? 'Moderate' : 'High'} drawdown risk
              </StatHelpText>
            </Stat>

            {/* Annualized Return */}
            <Stat>
              <StatLabel>
                <HStack>
                  <FiTrendingUp />
                  <Text>Annual Return</Text>
                </HStack>
              </StatLabel>
              <StatNumber color={metrics.annualized_return >= 0 ? 'green.500' : 'red.500'}>
                <StatArrow type={metrics.annualized_return >= 0 ? 'increase' : 'decrease'} />
                {formatPercentage(metrics.annualized_return)}
              </StatNumber>
              <StatHelpText>
                {metrics.annualized_return >= 0.12 ? 'Excellent' : 
                 metrics.annualized_return >= 0.08 ? 'Good' : 
                 metrics.annualized_return >= 0.04 ? 'Fair' : 'Poor'} performance
              </StatHelpText>
            </Stat>

            {/* Volatility */}
            <Stat>
              <StatLabel>
                <HStack>
                  <FiActivity />
                  <Text>Volatility</Text>
                </HStack>
              </StatLabel>
              <StatNumber color="orange.500">
                {formatPercentage(metrics.annualized_volatility)}
              </StatNumber>
              <StatHelpText>
                {metrics.annualized_volatility <= 0.15 ? 'Low' : 
                 metrics.annualized_volatility <= 0.25 ? 'Moderate' : 'High'} volatility
              </StatHelpText>
            </Stat>

            {/* Best/Worst Day */}
            <Stat>
              <StatLabel>
                <HStack>
                  <FiBarChart3 />
                  <Text>Extreme Returns</Text>
                </HStack>
              </StatLabel>
              <StatNumber fontSize="lg">
                <Text color="green.500">Best: {formatPercentage(metrics.best_day_return)}</Text>
                <Text color="red.500">Worst: {formatPercentage(metrics.worst_day_return)}</Text>
              </StatNumber>
              <StatHelpText>
                Single-day performance extremes
              </StatHelpText>
            </Stat>
          </SimpleGrid>
        </CardBody>
      </Card>
    );
  };

  // Component: Risk Assessment Card
  const RiskAssessmentCard: React.FC<{ assessment: RiskAssessment; confidence: number }> = ({ 
    assessment, 
    confidence 
  }) => {
    return (
      <Card>
        <CardHeader>
          <HStack justify="space-between">
            <Heading size="md">Risk Assessment</Heading>
            <Badge 
              colorScheme={getRiskColor(assessment.risk_level)} 
              variant="solid"
              fontSize="sm"
              px={3}
              py={1}
            >
              {assessment.risk_level} Risk
            </Badge>
          </HStack>
        </CardHeader>
        <CardBody pt={0}>
          <VStack spacing={4} align="stretch">
            
            {/* Overall Narrative */}
            <Box>
              <Text fontSize="sm" fontWeight="semibold" mb={2}>Investment Analysis</Text>
              <Box 
                p={3} 
                bg="gray.50" 
                borderRadius="md" 
                fontSize="sm" 
                lineHeight="1.6"
                maxH="300px"
                overflowY="auto"
                whiteSpace="pre-wrap"
              >
                {assessment.overall_narrative}
              </Box>
            </Box>

            {/* Risk Factors */}
            <Box>
              <Text fontSize="sm" fontWeight="semibold" mb={2}>Key Risk Factors</Text>
              <Wrap>
                {assessment.risk_factors.map((factor, index) => (
                  <WrapItem key={index}>
                    <Badge 
                      colorScheme="red" 
                      variant="subtle" 
                      fontSize="xs"
                      p={2}
                      borderRadius="md"
                    >
                      <HStack spacing={1}>
                        <FiAlertTriangle size={12} />
                        <Text>{factor}</Text>
                      </HStack>
                    </Badge>
                  </WrapItem>
                ))}
              </Wrap>
            </Box>

            {/* Detailed Assessments */}
            <Accordion allowToggle size="sm">
              <AccordionItem border="none">
                <AccordionButton px={0}>
                  <Text fontSize="sm" fontWeight="semibold">Detailed Analysis</Text>
                  <AccordionIcon />
                </AccordionButton>
                <AccordionPanel pb={0}>
                  <VStack spacing={3} align="stretch">
                    <Box>
                      <Text fontSize="sm" fontWeight="semibold" color="blue.600">Return Profile</Text>
                      <Text fontSize="sm" color="gray.700">{assessment.return_assessment}</Text>
                    </Box>
                    <Box>
                      <Text fontSize="sm" fontWeight="semibold" color="orange.600">Risk Characteristics</Text>
                      <Text fontSize="sm" color="gray.700">{assessment.volatility_assessment}</Text>
                    </Box>
                    <Box>
                      <Text fontSize="sm" fontWeight="semibold" color="purple.600">Drawdown Analysis</Text>
                      <Text fontSize="sm" color="gray.700">{assessment.drawdown_assessment}</Text>
                    </Box>
                  </VStack>
                </AccordionPanel>
              </AccordionItem>
            </Accordion>

            {/* Investment Recommendation */}
            <Alert status={getRiskColor(assessment.risk_level) === 'green' ? 'success' : 
                          getRiskColor(assessment.risk_level) === 'yellow' ? 'warning' : 'error'}>
              <AlertIcon />
              <Box>
                <AlertTitle fontSize="sm">Investment Recommendation</AlertTitle>
                <AlertDescription fontSize="sm">
                  {assessment.investment_recommendation}
                </AlertDescription>
              </Box>
            </Alert>

            {/* Confidence Level */}
            <Box>
              <HStack justify="space-between" mb={2}>
                <Text fontSize="sm" fontWeight="semibold">Analysis Confidence</Text>
                <Text fontSize="sm" color="gray.600">{confidence.toFixed(1)}%</Text>
              </HStack>
              <Progress 
                value={confidence} 
                colorScheme={confidence >= 80 ? 'green' : confidence >= 60 ? 'yellow' : 'red'}
                size="sm"
                borderRadius="md"
              />
            </Box>
          </VStack>
        </CardBody>
      </Card>
    );
  };

  // Component: Market Context Card
  const MarketContextCard: React.FC<{ context: MarketContext }> = ({ context }) => {
    return (
      <Card>
        <CardHeader>
          <Heading size="md">Market Context</Heading>
        </CardHeader>
        <CardBody pt={0}>
          <VStack spacing={4} align="stretch">
            
            {/* Data Source & Period */}
            <SimpleGrid columns={2} spacing={4}>
              <Box>
                <Text fontSize="sm" fontWeight="semibold">Data Source</Text>
                <HStack>
                  <Badge colorScheme={context.data_source === 'real' ? 'green' : 'blue'} variant="subtle">
                    {context.data_source.toUpperCase()}
                  </Badge>
                </HStack>
              </Box>
              <Box>
                <Text fontSize="sm" fontWeight="semibold">Analysis Period</Text>
                <Text fontSize="sm">{context.analysis_period}</Text>
              </Box>
            </SimpleGrid>

            {/* Price Range */}
            <Box>
              <Text fontSize="sm" fontWeight="semibold" mb={2}>Price Range (3 Years)</Text>
              <HStack justify="space-between" p={3} bg="gray.50" borderRadius="md">
                <VStack align="start" spacing={0}>
                  <Text fontSize="xs" color="gray.600">Minimum</Text>
                  <Text fontSize="sm" fontWeight="bold">${context.price_range.min.toFixed(2)}</Text>
                </VStack>
                <VStack align="start" spacing={0}>
                  <Text fontSize="xs" color="gray.600">Current</Text>
                  <Text fontSize="sm" fontWeight="bold">${context.price_range.current.toFixed(2)}</Text>
                </VStack>
                <VStack align="start" spacing={0}>
                  <Text fontSize="xs" color="gray.600">Maximum</Text>
                  <Text fontSize="sm" fontWeight="bold">${context.price_range.max.toFixed(2)}</Text>
                </VStack>
              </HStack>
            </Box>

            {/* Trading Statistics */}
            <Box>
              <Text fontSize="sm" fontWeight="semibold" mb={2}>Statistical Summary</Text>
              <SimpleGrid columns={2} spacing={3}>
                <Box>
                  <Text fontSize="xs" color="gray.600">Trading Days</Text>
                  <Text fontSize="sm" fontWeight="bold">{context.trading_days_analyzed}</Text>
                </Box>
                <Box>
                  <Text fontSize="xs" color="gray.600">Avg Daily Return</Text>
                  <Text fontSize="sm" fontWeight="bold">
                    {formatPercentage(context.return_distribution.mean)}
                  </Text>
                </Box>
                <Box>
                  <Text fontSize="xs" color="gray.600">Daily Volatility</Text>
                  <Text fontSize="sm" fontWeight="bold">
                    {formatPercentage(context.return_distribution.std)}
                  </Text>
                </Box>
                <Box>
                  <Text fontSize="xs" color="gray.600">Distribution Shape</Text>
                  <Text fontSize="sm" fontWeight="bold">
                    Skew: {context.return_distribution.skewness.toFixed(2)}
                  </Text>
                </Box>
              </SimpleGrid>
            </Box>
          </VStack>
        </CardBody>
      </Card>
    );
  };

  // Component: Comparison Results
  const ComparisonResults: React.FC<{ results: TickerComparison[] }> = ({ results }) => {
    if (results.length === 0) return null;

    return (
      <Card>
        <CardHeader>
          <Heading size="md">Ticker Comparison</Heading>
        </CardHeader>
        <CardBody pt={0}>
          <Box overflowX="auto">
            <Table variant="simple" size="sm">
              <Thead>
                <Tr>
                  <Th>Ticker</Th>
                  <Th>Sharpe</Th>
                  <Th>Sortino</Th>
                  <Th>Max DD</Th>
                  <Th>Ann Return</Th>
                  <Th>Risk Level</Th>
                </Tr>
              </Thead>
              <Tbody>
                {results.map((result, index) => (
                  <Tr key={index}>
                    <Td>
                      <HStack>
                        <Text fontWeight="bold">{result.ticker}</Text>
                        <Badge 
                          size="sm" 
                          colorScheme={result.data_source === 'real' ? 'green' : 'blue'}
                        >
                          {result.data_source}
                        </Badge>
                      </HStack>
                    </Td>
                    <Td>
                      <Text color={
                        getMetricStatus(result.sharpe_ratio, {good: 1.0, fair: 0.5}) === 'good' ? 'green.500' :
                        getMetricStatus(result.sharpe_ratio, {good: 1.0, fair: 0.5}) === 'fair' ? 'yellow.500' : 'red.500'
                      }>
                        {formatRatio(result.sharpe_ratio)}
                      </Text>
                    </Td>
                    <Td>
                      <Text color={
                        getMetricStatus(result.sortino_ratio, {good: 1.5, fair: 1.0}) === 'good' ? 'green.500' :
                        getMetricStatus(result.sortino_ratio, {good: 1.5, fair: 1.0}) === 'fair' ? 'yellow.500' : 'red.500'
                      }>
                        {formatRatio(result.sortino_ratio)}
                      </Text>
                    </Td>
                    <Td>
                      <Text color="red.500">
                        {formatPercentage(result.max_drawdown)}
                      </Text>
                    </Td>
                    <Td>
                      <Text color={result.annualized_return >= 0 ? 'green.500' : 'red.500'}>
                        {formatPercentage(result.annualized_return)}
                      </Text>
                    </Td>
                    <Td>
                      <Badge 
                        colorScheme={getRiskColor(result.risk_level)} 
                        variant="subtle"
                      >
                        {result.risk_level}
                      </Badge>
                    </Td>
                  </Tr>
                ))}
              </Tbody>
            </Table>
          </Box>
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
                  <Heading size="lg">Market Volatility Forecaster</Heading>
                  <Text color="gray.600">
                    Advanced risk analysis with Sharpe Ratio, Sortino Ratio, and Maximum Drawdown
                  </Text>
                </VStack>
                <HStack>
                  <Button
                    leftIcon={<FiRefreshCw />}
                    variant="ghost"
                    size="sm"
                    onClick={loadMarketIndicators}
                  >
                    Refresh Market Data
                  </Button>
                  <Button
                    leftIcon={<FiExternalLink />}
                    variant="outline"
                    size="sm"
                    onClick={onOpen}
                  >
                    Documentation
                  </Button>
                </HStack>
              </HStack>

              <HStack spacing={4} w="full">
                <Input
                  placeholder="Enter ticker symbol (e.g., AAPL, TSLA)"
                  value={ticker}
                  onChange={(e) => setTicker(e.target.value.toUpperCase())}
                  size="lg"
                  flex={2}
                  onKeyPress={(e) => e.key === 'Enter' && !isAnalyzing && analyzeTicker()}
                />
                <Select
                  value={analysisPeriod}
                  onChange={(e) => setAnalysisPeriod(e.target.value)}
                  size="lg"
                  flex={1}
                >
                  <option value="1y">1 Year</option>
                  <option value="2y">2 Years</option>
                  <option value="3y">3 Years</option>
                  <option value="5y">5 Years</option>
                </Select>
                <Button
                  leftIcon={isAnalyzing ? <Spinner size="sm" /> : <FiActivity />}
                  colorScheme="blue"
                  size="lg"
                  onClick={analyzeTicker}
                  isLoading={isAnalyzing}
                  loadingText="Analyzing..."
                >
                  Analyze
                </Button>
              </HStack>
            </VStack>
          </CardBody>
        </Card>

        {/* Analysis Parameters */}
        <Card>
          <CardHeader>
            <Heading size="sm">Analysis Parameters</Heading>
          </CardHeader>
          <CardBody pt={0}>
            <HStack spacing={6}>
              <FormControl maxW="200px">
                <FormLabel fontSize="sm">Risk-Free Rate</FormLabel>
                <NumberInput
                  value={riskFreeRate}
                  onChange={(valueString) => setRiskFreeRate(parseFloat(valueString) || 0.02)}
                  min={0}
                  max={0.10}
                  step={0.005}
                  precision={3}
                >
                  <NumberInputField />
                  <NumberInputStepper>
                    <NumberIncrementStepper />
                    <NumberDecrementStepper />
                  </NumberInputStepper>
                </NumberInput>
                <Text fontSize="xs" color="gray.500" mt={1}>
                  Annual risk-free rate (default: 2%)
                </Text>
              </FormControl>
              
              <Divider orientation="vertical" />

              <VStack align="start" spacing={2}>
                <Text fontSize="sm" fontWeight="semibold">Analysis Metrics</Text>
                <VStack align="start" spacing={1}>
                  <HStack>
                    <FiTrendingUp size={16} />
                    <Text fontSize="sm">Sharpe Ratio (risk-adjusted returns)</Text>
                  </HStack>
                  <HStack>
                    <FiShield size={16} />
                    <Text fontSize="sm">Sortino Ratio (downside risk focus)</Text>
                  </HStack>
                  <HStack>
                    <FiMaxDrawdown size={16} />
                    <Text fontSize="sm">Maximum Drawdown (peak-to-trough)</Text>
                  </HStack>
                </VStack>
              </VStack>
            </HStack>
          </CardBody>
        </Card>

        {/* Main Content */}
        <Grid templateColumns={{ base: '1fr', lg: '1fr 400px' }} gap={6}>
          
          {/* Left Column: Analysis Results */}
          <VStack spacing={6} align="stretch">
            
            {/* Current Analysis */}
            {currentAnalysis && (
              <VStack spacing={6} align="stretch">
                <Card>
                  <CardBody>
                    <HStack justify="space-between" mb={4}>
                      <VStack align="start" spacing={1}>
                        <Heading size="lg">{currentAnalysis.ticker} Analysis</Heading>
                        <Text fontSize="sm" color="gray.600">
                          Analysis completed: {new Date(currentAnalysis.analysis_timestamp).toLocaleString()}
                        </Text>
                      </VStack>
                      <VStack align="end" spacing={1}>
                        <Badge colorScheme="green" variant="solid" fontSize="sm" px={3}>
                          <HStack spacing={1}>
                            <FiCheckCircle size={14} />
                            <Text>Complete</Text>
                          </HStack>
                        </Badge>
                        <Text fontSize="xs" color="gray.500">
                          {currentAnalysis.confidence_level.toFixed(1)}% confidence
                        </Text>
                      </VStack>
                    </HStack>
                  </CardBody>
                </Card>

                <RiskMetricsCard metrics={currentAnalysis.risk_metrics} />
                <RiskAssessmentCard 
                  assessment={currentAnalysis.risk_assessment} 
                  confidence={currentAnalysis.confidence_level}
                />
                <MarketContextCard context={currentAnalysis.market_context} />
              </VStack>
            )}

            {/* Ticker Comparison */}
            {comparisonResults.length > 0 && (
              <ComparisonResults results={comparisonResults} />
            )}

            {/* Processing Indicator */}
            {(isAnalyzing || isComparing) && (
              <Card>
                <CardBody>
                  <VStack spacing={4}>
                    <Spinner size="xl" color="blue.500" />
                    <Text fontWeight="semibold">
                      {isAnalyzing ? 'Analyzing market volatility...' : 'Comparing tickers...'}
                    </Text>
                    <Text fontSize="sm" color="gray.600" textAlign="center">
                      Calculating risk metrics and generating comprehensive assessment
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
            
            {/* Market Indicators */}
            {marketIndicators && (
              <Card>
                <CardHeader>
                  <Heading size="sm">Market Indicators</Heading>
                </CardHeader>
                <CardBody pt={0}>
                  <VStack spacing={3} align="stretch">
                    <Box>
                      <HStack justify="space-between">
                        <Text fontSize="sm">Market Sentiment</Text>
                        <Text fontSize="sm" fontWeight="bold">
                          {(marketIndicators.market_sentiment.value * 100).toFixed(1)}%
                        </Text>
                      </HStack>
                      <Progress 
                        value={marketIndicators.market_sentiment.value * 100} 
                        colorScheme="blue" 
                        size="sm" 
                        mt={1}
                      />
                    </Box>
                    
                    <Box>
                      <HStack justify="space-between">
                        <Text fontSize="sm">Volatility Index</Text>
                        <Text fontSize="sm" fontWeight="bold">
                          {(marketIndicators.volatility_index.value * 100).toFixed(1)}%
                        </Text>
                      </HStack>
                      <Progress 
                        value={marketIndicators.volatility_index.value * 100} 
                        colorScheme="orange" 
                        size="sm" 
                        mt={1}
                      />
                    </Box>

                    <Divider />

                    <Box>
                      <Text fontSize="sm" fontWeight="semibold" mb={2}>Interest Rates</Text>
                      <VStack spacing={1}>
                        <HStack justify="space-between" w="full">
                          <Text fontSize="sm">Federal Funds</Text>
                          <Text fontSize="sm" fontWeight="bold">
                            {(marketIndicators.interest_rates.federal_funds * 100).toFixed(2)}%
                          </Text>
                        </HStack>
                        <HStack justify="space-between" w="full">
                          <Text fontSize="sm">10-Year Treasury</Text>
                          <Text fontSize="sm" fontWeight="bold">
                            {(marketIndicators.interest_rates.十年国债 * 100).toFixed(2)}%
                          </Text>
                        </HStack>
                      </VStack>
                    </Box>
                  </VStack>
                </CardBody>
              </Card>
            )}

            {/* Ticker Comparison */}
            <Card>
              <CardHeader>
                <Heading size="sm">Compare Tickers</Heading>
              </CardHeader>
              <CardBody pt={0}>
                <VStack spacing={4} align="stretch">
                  <Input
                    placeholder="Enter tickers separated by commas (e.g., AAPL,MSFT,GOOGL)"
                    value={comparisonTickers}
                    onChange={(e) => setComparisonTickers(e.target.value.toUpperCase())}
                    size="sm"
                  />
                  <Button
                    size="sm"
                    colorScheme="purple"
                    onClick={compareTickers}
                    isLoading={isComparing}
                    loadingText="Comparing..."
                    leftIcon={<FiBarChart3 />}
                  >
                    Compare Tickers
                  </Button>
                  <Text fontSize="xs" color="gray.500">
                    Compare up to 5 tickers side by side
                  </Text>
                </VStack>
              </CardBody>
            </Card>

            {/* Popular Tickers */}
            <Card>
              <CardHeader>
                <Heading size="sm">Popular Tickers</Heading>
              </CardHeader>
              <CardBody pt={0}>
                <VStack spacing={3} align="stretch">
                  {Object.entries(supportedTickers).map(([sector, tickers]: [string, any]) => (
                    <Box key={sector}>
                      <Text fontSize="sm" fontWeight="semibold" mb={1} color="blue.600">
                        {sector}
                      </Text>
                      <Wrap>
                        {tickers.map((ticker: string) => (
                          <WrapItem key={ticker}>
                            <Button
                              size="xs"
                              variant="outline"
                              onClick={() => setTicker(ticker)}
                            >
                              {ticker}
                            </Button>
                          </WrapItem>
                        ))}
                      </Wrap>
                    </Box>
                  ))}
                </VStack>
              </CardBody>
            </Card>

            {/* Analysis History */}
            <Card>
              <CardHeader>
                <Heading size="sm">Recent Analysis</Heading>
              </CardHeader>
              <CardBody pt={0}>
                <VStack spacing={2} align="stretch">
                  {analysisHistory.length === 0 ? (
                    <Text fontSize="sm" color="gray.500" textAlign="center" py={4}>
                      No analysis history yet
                    </Text>
                  ) : (
                    analysisHistory.slice(0, 5).map((analysis, index) => (
                      <HStack
                        key={index}
                        p={2}
                        borderRadius="md"
                        bg="gray.50"
                        justify="space-between"
                      >
                        <VStack align="start" spacing={0}>
                          <Text fontSize="sm" fontWeight="bold">
                            {analysis.ticker}
                          </Text>
                          <Text fontSize="xs" color="gray.500">
                            {analysis.analysis_period}
                          </Text>
                        </VStack>
                        <Text fontSize="xs" color="gray.500">
                          {new Date(analysis.timestamp).toLocaleDateString()}
                        </Text>
                      </HStack>
                    ))
                  )}
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
          <ModalHeader>Market Volatility Forecaster Documentation</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <VStack spacing={6} align="stretch">
              
              <Box>
                <Heading size="md" mb={3}>Risk Metrics Explained</Heading>
                <VStack spacing={4} align="stretch">
                  <Box>
                    <Text fontWeight="semibold" color="blue.600">Sharpe Ratio</Text>
                    <Text fontSize="sm">
                      Measures risk-adjusted returns by comparing excess returns to volatility. 
                      Higher values indicate better risk-adjusted performance. Values above 1.0 are considered excellent.
                    </Text>
                  </Box>
                  <Box>
                    <Text fontWeight="semibold" color="green.600">Sortino Ratio</Text>
                    <Text fontSize="sm">
                      Similar to Sharpe ratio but only considers downside volatility. 
                      Provides a more accurate measure for risk-averse investors. Values above 1.5 are excellent.
                    </Text>
                  </Box>
                  <Box>
                    <Text fontWeight="semibold" color="red.600">Maximum Drawdown</Text>
                    <Text fontSize="sm">
                      The largest peak-to-trough decline during the analysis period. 
                      Indicates the worst-case loss an investor would have experienced. Lower values indicate better downside protection.
                    </Text>
                  </Box>
                </VStack>
              </Box>

              <Divider />

              <Box>
                <Heading size="md" mb={3}>Risk Assessment Levels</Heading>
                <VStack spacing={3} align="stretch">
                  <HStack>
                    <Badge colorScheme="green" variant="solid">Low Risk</Badge>
                    <Text fontSize="sm">Stable returns with minimal volatility, suitable for conservative portfolios</Text>
                  </HStack>
                  <HStack>
                    <Badge colorScheme="yellow" variant="solid">Moderate Risk</Badge>
                    <Text fontSize="sm">Balanced risk-return profile, appropriate for diversified portfolios</Text>
                  </HStack>
                  <HStack>
                    <Badge colorScheme="orange" variant="solid">High Risk</Badge>
                    <Text fontSize="sm">Higher volatility with growth potential, suitable for aggressive strategies</Text>
                  </HStack>
                  <HStack>
                    <Badge colorScheme="red" variant="solid">Very High Risk</Badge>
                    <Text fontSize="sm">Extreme volatility requiring careful risk management and diversification</Text>
                  </HStack>
                </VStack>
              </Box>

              <Divider />

              <Box>
                <Heading size="md" mb={3}>Data Sources</Heading>
                <Text fontSize="sm" mb={2}>
                  The analysis uses multiple data sources depending on availability:
                </Text>
                <VStack spacing={2} align="stretch">
                  <HStack>
                    <Badge colorScheme="green">Real Data</Badge>
                    <Text fontSize="sm">Live market data from Yahoo Finance API</Text>
                  </HStack>
                  <HStack>
                    <Badge colorScheme="blue">Simulated Data</Badge>
                    <Text fontSize="sm">Realistic market scenarios based on historical patterns</Text>
                  </HStack>
                </VStack>
              </Box>

              <Divider />

              <Box>
                <Heading size="md" mb={3}>Investment Disclaimer</Heading>
                <Alert status="warning">
                  <AlertIcon />
                  <Box>
                    <Text fontSize="sm">
                      This analysis is for educational and informational purposes only. 
                      It should not be considered as financial advice. Always consult with 
                      a qualified financial advisor before making investment decisions.
                    </Text>
                  </Box>
                </Alert>
              </Box>
            </VStack>
          </ModalBody>
          <ModalFooter>
            <Button onClick={onClose}>Close</Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </Box>
  );
};

export default MarketVolatilityForecaster;