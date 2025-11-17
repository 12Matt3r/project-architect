/**
 * Template #38: Unstructured Data Summarizer - React Frontend
 * 
 * Advanced text analysis interface for customer support ticket root cause identification.
 * Displays hidden patterns, supporting evidence, and actionable recommendations.
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
  Textarea,
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
  FormControl,
  FormLabel,
  Input,
  Select,
  Code,
  Link,
  AspectRatio,
  NumberInput,
  NumberInputField,
  NumberInputStepper,
  NumberIncrementStepper,
  NumberDecrementStepper,
  InputGroup,
  InputLeftElement,
  InputRightElement
} from '@chakra-ui/react';
import {
  FiSearch,
  FiFileText,
  FiTrendingUp,
  FiAlertTriangle,
  FiCheckCircle,
  FiMessageSquare,
  FiRefreshCw,
  FiDownload,
  FiShare2,
  FiInfo,
  FiClock,
  FiTarget,
  FiLayers,
  FiActivity,
  FiEye,
  FiEyeOff,
  FiMaximize2,
  FiPlus,
  FiMinus,
  FiUpload,
  FiDatabase,
  FiTrendingDown,
  FiBarChart3,
  FiFilter,
  FiBook,
  FiCode,
  FiLightbulb
} from 'react-icons/fi';

// API Configuration
const API_BASE_URL = 'http://localhost:8000/api/v1';

// Types and Interfaces
interface Ticket {
  id: string;
  content: string;
  timestamp?: string;
  customer_id?: string;
  category?: string;
  priority?: string;
}

interface RootCauseAnalysis {
  analysis_id: string;
  total_tickets: number;
  root_cause_statement: string;
  confidence_score: number;
  supporting_evidence: string[];
  pattern_analysis: {
    topic_frequencies: Record<string, number>;
    keyword_cooccurrence: Record<string, Record<string, number>>;
    sentiment_trends: number[];
    entity_mentions: Record<string, string[]>;
    urgency_patterns: string[];
    temporal_patterns: Record<string, number>;
  };
  topic_frequency: Record<string, number>;
  sentiment_analysis: {
    overall_sentiment: number;
    sentiment_distribution: Record<string, number>;
    sentiment_trend: string;
  };
  keywords_identified: string[];
  processing_metadata: {
    processing_time: number;
    tickets_processed: number;
    candidates_identified: number;
  };
  created_at: string;
}

interface AnalysisResponse {
  success: boolean;
  root_cause: RootCauseAnalysis;
  summary: Record<string, any>;
  recommendations: string[];
  processing_time: number;
}

// Main Component
const UnstructuredDataSummarizer: React.FC = () => {
  // State Management
  const [ticketsText, setTicketsText] = useState('');
  const [ticketsJson, setTicketsJson] = useState('');
  const [inputMode, setInputMode] = useState<'text' | 'json'>('text');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [currentAnalysis, setCurrentAnalysis] = useState<AnalysisResponse | null>(null);
  const [sampleTickets, setSampleTickets] = useState<Ticket[]>([]);
  const [analysisHistory, setAnalysisHistory] = useState<any[]>([]);
  const [showSampleData, setShowSampleData] = useState(false);
  const [selectedEvidence, setSelectedEvidence] = useState<number | null>(null);
  const [expandedSections, setExpandedSections] = useState<string[]>(['root-cause']);
  
  // Hooks
  const toast = useToast();
  const { isOpen, onOpen, onClose } = useDisclosure();
  const { isOpen: isHistoryOpen, onOpen: onHistoryOpen, onClose: onHistoryClose } = useDisclosure();

  // Load initial data
  useEffect(() => {
    loadSampleTickets();
    loadAnalysisHistory();
  }, []);

  // API Functions
  const loadSampleTickets = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/sample-tickets`);
      const data = await response.json();
      setSampleTickets(data.sample_tickets || []);
    } catch (error) {
      console.error('Failed to load sample tickets:', error);
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

  const analyzeSampleTickets = async () => {
    setIsAnalyzing(true);

    try {
      const response = await fetch(`${API_BASE_URL}/analyze-sample`, {
        method: 'POST',
      });

      if (!response.ok) {
        throw new Error('Sample analysis failed');
      }

      const data: AnalysisResponse = await response.json();
      setCurrentAnalysis(data);
      loadAnalysisHistory();

      toast({
        title: 'Sample Analysis Complete',
        description: 'Root cause analysis of sample tickets completed successfully',
        status: 'success',
        duration: 3000,
        isClosable: true
      });

    } catch (error) {
      toast({
        title: 'Analysis Error',
        description: 'Failed to analyze sample tickets. Please try again.',
        status: 'error',
        duration: 5000,
        isClosable: true
      });
    } finally {
      setIsAnalyzing(false);
    }
  };

  const analyzeCustomTickets = async () => {
    if (!ticketsText.trim() && !ticketsJson.trim()) {
      toast({
        title: 'Tickets Required',
        description: 'Please provide customer support tickets to analyze',
        status: 'warning',
        duration: 3000,
        isClosable: true
      });
      return;
    }

    setIsAnalyzing(true);

    try {
      const payload = inputMode === 'json' ? ticketsJson : ticketsText;

      const response = await fetch(`${API_BASE_URL}/upload-tickets`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          tickets_text: payload
        }),
      });

      if (!response.ok) {
        throw new Error('Custom analysis failed');
      }

      const data: AnalysisResponse = await response.json();
      setCurrentAnalysis(data);
      loadAnalysisHistory();

      toast({
        title: 'Analysis Complete',
        description: 'Root cause analysis completed successfully',
        status: 'success',
        duration: 3000,
        isClosable: true
      });

    } catch (error) {
      toast({
        title: 'Analysis Error',
        description: 'Failed to analyze tickets. Please check your input format.',
        status: 'error',
        duration: 5000,
        isClosable: true
      });
    } finally {
      setIsAnalyzing(false);
    }
  };

  // Utility Functions
  const getSentimentColor = (sentiment: number) => {
    if (sentiment > 0.1) return 'green';
    if (sentiment < -0.1) return 'red';
    return 'gray';
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return 'green';
    if (confidence >= 0.6) return 'yellow';
    if (confidence >= 0.4) return 'orange';
    return 'red';
  };

  const getSentimentLabel = (sentiment: number) => {
    if (sentiment > 0.5) return 'Very Positive';
    if (sentiment > 0.1) return 'Positive';
    if (sentiment < -0.5) return 'Very Negative';
    if (sentiment < -0.1) return 'Negative';
    return 'Neutral';
  };

  const formatProcessingTime = (seconds: number) => {
    if (seconds < 1) return `${(seconds * 1000).toFixed(0)}ms`;
    return `${seconds.toFixed(2)}s`;
  };

  // Component: Ticket Input Section
  const TicketInputSection: React.FC = () => {
    const loadSampleIntoInput = () => {
      const sampleText = sampleTickets.map(ticket => ticket.content).join('\n\n');
      setTicketsText(sampleText);
      setInputMode('text');
      setShowSampleData(false);
    };

    return (
      <Card>
        <CardHeader>
          <HStack justify="space-between">
            <VStack align="start" spacing={1}>
              <Heading size="md">Customer Support Tickets</Heading>
              <Text fontSize="sm" color="gray.600">
                Upload or paste customer support tickets for root cause analysis
              </Text>
            </VStack>
            <HStack>
              <Button
                size="sm"
                variant="outline"
                leftIcon={<FiDatabase />}
                onClick={() => setShowSampleData(!showSampleData)}
              >
                Sample Data
              </Button>
              <Button
                size="sm"
                variant="outline"
                leftIcon={<FiBook />}
                onClick={onOpen}
              >
                Format Guide
              </Button>
            </HStack>
          </HStack>
        </CardHeader>
        <CardBody pt={0}>
          <VStack spacing={4} align="stretch">
            
            {/* Input Mode Toggle */}
            <HStack>
              <Button
                size="sm"
                variant={inputMode === 'text' ? 'solid' : 'outline'}
                onClick={() => setInputMode('text')}
              >
                Plain Text
              </Button>
              <Button
                size="sm"
                variant={inputMode === 'json' ? 'solid' : 'outline'}
                onClick={() => setInputMode('json')}
              >
                JSON Format
              </Button>
            </HStack>

            {/* Sample Data Display */}
            {showSampleData && (
              <Card size="sm" variant="outline" bg="blue.50">
                <CardBody pt={3}>
                  <VStack spacing={3} align="stretch">
                    <HStack justify="space-between">
                      <Text fontSize="sm" fontWeight="semibold">
                        Sample Customer Support Tickets ({sampleTickets.length} tickets)
                      </Text>
                      <HStack>
                        <Button
                          size="xs"
                          onClick={loadSampleIntoInput}
                          leftIcon={<FiPlus />}
                        >
                          Load to Input
                        </Button>
                        <Button
                          size="xs"
                          variant="outline"
                          onClick={analyzeSampleTickets}
                          isLoading={isAnalyzing}
                          loadingText="Analyzing..."
                        >
                          Analyze Sample
                        </Button>
                      </HStack>
                    </HStack>
                    <Box maxH="200px" overflowY="auto">
                      <VStack spacing={2} align="stretch">
                        {sampleTickets.map((ticket, index) => (
                          <Box key={ticket.id} p={2} bg="white" borderRadius="md" fontSize="sm">
                            <HStack justify="space-between" mb={1}>
                              <Text fontWeight="bold">{ticket.id}</Text>
                              <Text fontSize="xs" color="gray.500">
                                {ticket.timestamp?.split('T')[0]}
                              </Text>
                            </HStack>
                            <Text noOfLines={3}>{ticket.content}</Text>
                          </Box>
                        ))}
                      </VStack>
                    </Box>
                  </VStack>
                </CardBody>
              </Card>
            )}

            {/* Input Textarea */}
            {inputMode === 'text' ? (
              <FormControl>
                <FormLabel fontSize="sm">Paste customer support tickets (one per line or paragraph)</FormLabel>
                <Textarea
                  value={ticketsText}
                  onChange={(e) => setTicketsText(e.target.value)}
                  placeholder={`Enter customer support tickets here...

Example:
"I can't log into my account. The login page shows an error when I enter my password."
"The checkout process is broken. The page freezes when I try to complete my purchase."
"My payment was declined but funds were charged to my account."`}
                  rows={10}
                  fontSize="sm"
                />
                <Text fontSize="xs" color="gray.500" mt={1}>
                  You can paste up to 10 tickets. Each ticket should be on a separate line or paragraph.
                </Text>
              </FormControl>
            ) : (
              <FormControl>
                <FormLabel fontSize="sm">JSON array of ticket objects</FormLabel>
                <Textarea
                  value={ticketsJson}
                  onChange={(e) => setTicketsJson(e.target.value)}
                  placeholder={`[
  {
    "id": "T001",
    "content": "I can't log into my account. The login page shows an error when I enter my password.",
    "timestamp": "2025-11-15T10:30:00Z"
  },
  {
    "id": "T002", 
    "content": "The checkout process is broken. The page freezes when I try to complete my purchase.",
    "timestamp": "2025-11-15T11:15:00Z"
  }
]`}
                  rows={10}
                  fontSize="sm"
                />
                <Text fontSize="xs" color="gray.500" mt={1}>
                  JSON format allows additional metadata like IDs, timestamps, categories, and priorities.
                </Text>
              </FormControl>
            )}

            {/* Action Buttons */}
            <HStack justify="space-between">
              <HStack>
                <Button
                  size="sm"
                  variant="outline"
                  leftIcon={<FiRefreshCw />}
                  onClick={() => {
                    setTicketsText('');
                    setTicketsJson('');
                    setCurrentAnalysis(null);
                  }}
                >
                  Clear
                </Button>
                <Button
                  size="sm"
                  variant="outline"
                  leftIcon={<FiDownload />}
                  onClick={() => toast({
                    title: 'Feature Coming Soon',
                    description: 'Export functionality will be available in the next update',
                    status: 'info',
                    duration: 3000
                  })}
                >
                  Export
                </Button>
              </HStack>
              
              <Button
                colorScheme="blue"
                onClick={analyzeCustomTickets}
                isLoading={isAnalyzing}
                loadingText="Analyzing..."
                leftIcon={isAnalyzing ? <Spinner size="sm" /> : <FiSearch />}
                isDisabled={!ticketsText.trim() && !ticketsJson.trim()}
              >
                Analyze Tickets
              </Button>
            </HStack>
          </VStack>
        </CardBody>
      </Card>
    );
  };

  // Component: Root Cause Display
  const RootCauseDisplay: React.FC<{ analysis: AnalysisResponse }> = ({ analysis }) => {
    const { root_cause } = analysis;

    return (
      <Card>
        <CardHeader>
          <HStack justify="space-between">
            <VStack align="start" spacing={1}>
              <Heading size="lg">Root Cause Analysis</Heading>
              <Text fontSize="sm" color="gray.600">
                Analysis completed in {formatProcessingTime(analysis.processing_time)}
              </Text>
            </VStack>
            <VStack align="end" spacing={1}>
              <Badge 
                colorScheme={getConfidenceColor(root_cause.confidence_score)} 
                variant="solid"
                fontSize="sm"
                px={3}
                py={1}
              >
                {root_cause.confidence_score.toFixed(1)}% Confidence
              </Badge>
              <Text fontSize="xs" color="gray.500">
                {root_cause.total_tickets} tickets analyzed
              </Text>
            </VStack>
          </HStack>
        </CardHeader>
        <CardBody pt={0}>
          <VStack spacing={6} align="stretch">
            
            {/* Main Root Cause Statement */}
            <Box>
              <Text fontSize="lg" fontWeight="bold" mb={2}>Primary Root Cause</Text>
              <Box 
                p={4} 
                bg="red.50" 
                borderLeft="4px solid" 
                borderColor="red.400"
                borderRadius="md"
              >
                <Text fontSize="md" lineHeight="1.6">
                  {root_cause.root_cause_statement}
                </Text>
              </Box>
            </Box>

            {/* Confidence Metrics */}
            <SimpleGrid columns={{ base: 1, md: 3 }} spacing={4}>
              <Stat>
                <StatLabel>
                  <HStack>
                    <FiTarget />
                    <Text>Confidence Score</Text>
                  </HStack>
                </StatLabel>
                <StatNumber color={`${getConfidenceColor(root_cause.confidence_score)}.500`}>
                  {(root_cause.confidence_score * 100).toFixed(1)}%
                </StatNumber>
                <StatHelpText>
                  {root_cause.confidence_score >= 0.8 ? 'Very High' : 
                   root_cause.confidence_score >= 0.6 ? 'High' : 
                   root_cause.confidence_score >= 0.4 ? 'Medium' : 'Low'} confidence
                </StatHelpText>
              </Stat>

              <Stat>
                <StatLabel>
                  <HStack>
                    <FiFileText />
                    <Text>Tickets Processed</Text>
                  </HStack>
                </StatLabel>
                <StatNumber>{root_cause.total_tickets}</StatNumber>
                <StatHelpText>
                  {root_cause.processing_metadata.candidates_identified} patterns identified
                </StatHelpText>
              </Stat>

              <Stat>
                <StatLabel>
                  <HStack>
                    <FiCheckCircle />
                    <Text>Evidence Quotes</Text>
                  </HStack>
                </StatLabel>
                <StatNumber>{root_cause.supporting_evidence.length}</StatNumber>
                <StatHelpText>
                  Supporting evidence
                </StatHelpText>
              </Stat>
            </SimpleGrid>

            {/* Supporting Evidence */}
            <Box>
              <Text fontSize="md" fontWeight="bold" mb={3}>Supporting Evidence</Text>
              <VStack spacing={3} align="stretch">
                {root_cause.supporting_evidence.map((evidence, index) => (
                  <Card 
                    key={index} 
                    size="sm" 
                    variant="outline"
                    cursor="pointer"
                    onClick={() => setSelectedEvidence(selectedEvidence === index ? null : index)}
                    _hover={{ bg: 'gray.50' }}
                  >
                    <CardBody>
                      <HStack justify="space-between">
                        <Text fontSize="sm" flex={1} noOfLines={selectedEvidence === index ? undefined : 2}>
                          "{evidence}"
                        </Text>
                        <IconButton
                          size="sm"
                          variant="ghost"
                          icon={selectedEvidence === index ? <FiEyeOff /> : <FiEye />}
                          aria-label="Toggle evidence visibility"
                        />
                      </HStack>
                    </CardBody>
                  </Card>
                ))}
              </VStack>
            </Box>
          </VStack>
        </CardBody>
      </Card>
    );
  };

  // Component: Pattern Analysis
  const PatternAnalysisSection: React.FC<{ analysis: AnalysisResponse }> = ({ analysis }) => {
    const { root_cause } = analysis;
    const { pattern_analysis, sentiment_analysis, keywords_identified } = root_cause;

    return (
      <Card>
        <CardHeader>
          <Heading size="md">Pattern Analysis</Heading>
        </CardHeader>
        <CardBody pt={0}>
          <Accordion allowMultiple defaultIndex={[0, 1, 2]}>
            
            {/* Topic Frequency */}
            <AccordionItem border="none">
              <AccordionButton px={0}>
                <HStack flex="1" textAlign="left">
                  <FiLayers />
                  <Text fontWeight="semibold">Topic Frequency Analysis</Text>
                </HStack>
                <AccordionIcon />
              </AccordionButton>
              <AccordionPanel pb={0}>
                <VStack spacing={3} align="stretch">
                  {Object.entries(pattern_analysis.topic_frequencies)
                    .sort(([,a], [,b]) => b - a)
                    .slice(0, 8)
                    .map(([topic, count]) => (
                    <HStack key={topic} justify="space-between">
                      <Text fontSize="sm" textTransform="capitalize">{topic.replace('_', ' ')}</Text>
                      <HStack>
                        <Progress 
                          value={(count / Math.max(...Object.values(pattern_analysis.topic_frequencies))) * 100} 
                          w="100px" 
                          size="sm" 
                          colorScheme="blue"
                        />
                        <Text fontSize="sm" fontWeight="bold" minW="30px">{count}</Text>
                      </HStack>
                    </HStack>
                  ))}
                </VStack>
              </AccordionPanel>
            </AccordionItem>

            {/* Sentiment Analysis */}
            <AccordionItem border="none">
              <AccordionButton px={0}>
                <HStack flex="1" textAlign="left">
                  <FiActivity />
                  <Text fontWeight="semibold">Sentiment Analysis</Text>
                </HStack>
                <AccordionIcon />
              </AccordionButton>
              <AccordionPanel pb={0}>
                <VStack spacing={4} align="stretch">
                  <HStack justify="space-between">
                    <Text fontSize="sm">Overall Sentiment</Text>
                    <Badge 
                      colorScheme={getSentimentColor(sentiment_analysis.overall_sentiment)}
                      variant="solid"
                    >
                      {getSentimentLabel(sentiment_analysis.overall_sentiment)}
                    </Badge>
                  </HStack>
                  
                  <Box>
                    <Text fontSize="sm" mb={2}>Sentiment Distribution</Text>
                    <SimpleGrid columns={2} spacing={2}>
                      {Object.entries(sentiment_analysis.sentiment_distribution).map(([sentiment, count]) => (
                        <HStack key={sentiment} justify="space-between">
                          <Text fontSize="sm" textTransform="capitalize">{sentiment.replace('_', ' ')}</Text>
                          <Text fontSize="sm" fontWeight="bold">{count}</Text>
                        </HStack>
                      ))}
                    </SimpleGrid>
                  </Box>
                </VStack>
              </AccordionPanel>
            </AccordionItem>

            {/* Keywords */}
            <AccordionItem border="none">
              <AccordionButton px={0}>
                <HStack flex="1" textAlign="left">
                  <FiSearch />
                  <Text fontWeight="semibold">Key Terms Identified</Text>
                </HStack>
                <AccordionIcon />
              </AccordionButton>
              <AccordionPanel pb={0}>
                <Wrap>
                  {keywords_identified.slice(0, 15).map((keyword, index) => (
                    <WrapItem key={index}>
                      <Badge colorScheme="purple" variant="subtle" fontSize="xs">
                        {keyword}
                      </Badge>
                    </WrapItem>
                  ))}
                </Wrap>
              </AccordionPanel>
            </AccordionItem>
          </Accordion>
        </CardBody>
      </Card>
    );
  };

  // Component: Recommendations
  const RecommendationsSection: React.FC<{ analysis: AnalysisResponse }> = ({ analysis }) => {
    return (
      <Card>
        <CardHeader>
          <Heading size="md">Actionable Recommendations</Heading>
        </CardHeader>
        <CardBody pt={0}>
          <VStack spacing={4} align="stretch">
            {analysis.recommendations.map((recommendation, index) => (
              <Alert key={index} status="info" variant="left-accent">
                <AlertIcon />
                <Box>
                  <Text fontSize="sm">{recommendation}</Text>
                </Box>
              </Alert>
            ))}
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
                  <Heading size="lg">Unstructured Data Summarizer</Heading>
                  <Text color="gray.600">
                    AI-powered root cause analysis for customer support tickets
                  </Text>
                </VStack>
                <HStack>
                  <Button
                    leftIcon={<FiHistory />}
                    variant="ghost"
                    size="sm"
                    onClick={onHistoryOpen}
                  >
                    Analysis History
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
            </VStack>
          </CardBody>
        </Card>

        {/* Main Content */}
        <Grid templateColumns={{ base: '1fr', lg: '1fr 400px' }} gap={6}>
          
          {/* Left Column: Analysis Results */}
          <VStack spacing={6} align="stretch">
            
            {/* Ticket Input */}
            <TicketInputSection />

            {/* Analysis Results */}
            {currentAnalysis && (
              <VStack spacing={6} align="stretch">
                <RootCauseDisplay analysis={currentAnalysis} />
                <PatternAnalysisSection analysis={currentAnalysis} />
                <RecommendationsSection analysis={currentAnalysis} />
              </VStack>
            )}

            {/* Processing Indicator */}
            {isAnalyzing && (
              <Card>
                <CardBody>
                  <VStack spacing={4}>
                    <Spinner size="xl" color="blue.500" />
                    <Text fontWeight="semibold">Analyzing customer support tickets...</Text>
                    <Text fontSize="sm" color="gray.600" textAlign="center">
                      Processing text, identifying patterns, and generating root cause analysis
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
            
            {/* Analysis Overview */}
            {currentAnalysis && (
              <Card>
                <CardHeader>
                  <Heading size="sm">Analysis Overview</Heading>
                </CardHeader>
                <CardBody pt={0}>
                  <VStack spacing={3} align="stretch">
                    <Box>
                      <Text fontSize="sm" color="gray.600">Processing Time</Text>
                      <Text fontSize="sm" fontWeight="bold">
                        {formatProcessingTime(currentAnalysis.processing_time)}
                      </Text>
                    </Box>
                    
                    <Box>
                      <Text fontSize="sm" color="gray.600">Tickets Analyzed</Text>
                      <Text fontSize="sm" fontWeight="bold">
                        {currentAnalysis.root_cause.total_tickets}
                      </Text>
                    </Box>
                    
                    <Box>
                      <Text fontSize="sm" color="gray.600">Patterns Found</Text>
                      <Text fontSize="sm" fontWeight="bold">
                        {currentAnalysis.root_cause.processing_metadata.candidates_identified}
                      </Text>
                    </Box>
                    
                    <Box>
                      <Text fontSize="sm" color="gray.600">Evidence Quotes</Text>
                      <Text fontSize="sm" fontWeight="bold">
                        {currentAnalysis.root_cause.supporting_evidence.length}
                      </Text>
                    </Box>
                  </VStack>
                </CardBody>
              </Card>
            )}

            {/* Methodology */}
            <Card>
              <CardHeader>
                <Heading size="sm">Analysis Methodology</Heading>
              </CardHeader>
              <CardBody pt={0}>
                <VStack spacing={3} align="stretch">
                  <Text fontSize="sm">
                    Our AI-powered analysis uses advanced NLP techniques to identify hidden patterns:
                  </Text>
                  
                  <VStack spacing={2} align="stretch">
                    <HStack>
                      <Box w={3} h={3} bg="blue.400" borderRadius="full" />
                      <Text fontSize="sm"><strong>Pattern Recognition:</strong> Identifies recurring themes and issues</Text>
                    </HStack>
                    <HStack>
                      <Box w={3} h={3} bg="green.400" borderRadius="full" />
                      <Text fontSize="sm"><strong>Sentiment Analysis:</strong> Measures customer satisfaction levels</Text>
                    </HStack>
                    <HStack>
                      <Box w={3} h={3} bg="purple.400" borderRadius="full" />
                      <Text fontSize="sm"><strong>Keyword Extraction:</strong> Finds critical terms and phrases</Text>
                    </HStack>
                    <HStack>
                      <Box w={3} h={3} bg="orange.400" borderRadius="full" />
                      <Text fontSize="sm"><strong>Root Cause ID:</strong> Discovers underlying system issues</Text>
                    </HStack>
                  </VStack>
                </VStack>
              </CardBody>
            </Card>

            {/* Quick Actions */}
            <Card>
              <CardHeader>
                <Heading size="sm">Quick Actions</Heading>
              </CardHeader>
              <CardBody pt={0}>
                <VStack spacing={3} align="stretch">
                  <Button size="sm" variant="outline" leftIcon={<FiRefreshCw />}>
                    Re-analyze
                  </Button>
                  <Button size="sm" variant="outline" leftIcon={<FiDownload />}>
                    Export Report
                  </Button>
                  <Button size="sm" variant="outline" leftIcon={<FiShare2 />}>
                    Share Results
                  </Button>
                  <Button size="sm" variant="outline" leftIcon={<FiLightbulb />}>
                    Generate Insights
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
          <ModalHeader>Data Input Format Guide</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <VStack spacing={6} align="stretch">
              
              <Box>
                <Heading size="md" mb={3}>Supported Input Formats</Heading>
                <Tabs>
                  <TabList>
                    <Tab>Plain Text</Tab>
                    <Tab>JSON Format</Tab>
                  </TabList>
                  <TabPanels>
                    <TabPanel>
                      <VStack spacing={4} align="stretch">
                        <Box>
                          <Text fontWeight="semibold" mb={2}>Plain Text Format</Text>
                          <Text fontSize="sm" mb={3}>
                            Simply paste customer support tickets as plain text. Each ticket should be 
                            separated by a blank line or new paragraph.
                          </Text>
                          
                          <Box bg="gray.100" p={3} borderRadius="md" fontSize="sm">
                            <Text fontFamily="mono">
{`I can't log into my account. The login page keeps showing an error when I enter my password. This is very frustrating.

The checkout process is broken. When I try to complete my purchase, the page freezes and I get a timeout error.

My payment was declined but the funds were still charged to my account. I need this resolved immediately.`}
                            </Text>
                          </Box>
                        </Box>
                        
                        <Alert status="info">
                          <AlertIcon />
                          <Text fontSize="sm">
                            For best results, include the full customer message with context about the issue they're experiencing.
                          </Text>
                        </Alert>
                      </VStack>
                    </TabPanel>
                    
                    <TabPanel>
                      <VStack spacing={4} align="stretch">
                        <Box>
                          <Text fontWeight="semibold" mb={2}>JSON Format</Text>
                          <Text fontSize="sm" mb={3}>
                            Provide structured ticket data with optional metadata fields for richer analysis.
                          </Text>
                          
                          <Box bg="gray.100" p={3} borderRadius="md" fontSize="sm">
                            <Text fontFamily="mono">
{`[
  {
    "id": "T001",
    "content": "I can't log into my account. The login page shows an error when I enter my password.",
    "timestamp": "2025-11-15T10:30:00Z",
    "customer_id": "CUST123",
    "category": "Authentication",
    "priority": "High"
  },
  {
    "id": "T002",
    "content": "The checkout process is broken. The page freezes when I try to complete my purchase.",
    "timestamp": "2025-11-15T11:15:00Z",
    "category": "Payment",
    "priority": "Critical"
  }
]`}
                            </Text>
                          </Box>
                        </Box>
                        
                        <Box>
                          <Text fontWeight="semibold" mb={2}>Optional Fields</Text>
                          <VStack spacing={2} align="stretch" fontSize="sm">
                            <Text><code>id</code> - Unique identifier for the ticket</Text>
                            <Text><code>content</code> - The main customer message (required)</Text>
                            <Text><code>timestamp</code> - When the ticket was created</Text>
                            <Text><code>customer_id</code> - Customer identifier</Text>
                            <Text><code>category</code> - Ticket category or type</Text>
                            <Text><code>priority</code> - Priority level (Low, Medium, High, Critical)</Text>
                          </VStack>
                        </Box>
                      </VStack>
                    </TabPanel>
                  </TabPanels>
                </Tabs>
              </Box>

              <Divider />

              <Box>
                <Heading size="md" mb={3}>Analysis Process</Heading>
                <VStack spacing={3} align="stretch">
                  <Text fontSize="sm">
                    The system processes your tickets through several analysis stages:
                  </Text>
                  
                  <VStack spacing={2} align="stretch">
                    <HStack>
                      <Badge colorScheme="blue">1</Badge>
                      <Text fontSize="sm"><strong>Text Preprocessing:</strong> Clean and normalize ticket content</Text>
                    </HStack>
                    <HStack>
                      <Badge colorScheme="green">2</Badge>
                      <Text fontSize="sm"><strong>Pattern Recognition:</strong> Identify recurring themes and keywords</Text>
                    </HStack>
                    <HStack>
                      <Badge colorScheme="purple">3</Badge>
                      <Text fontSize="sm"><strong>Root Cause Analysis:</strong> Determine underlying system issues</Text>
                    </HStack>
                    <HStack>
                      <Badge colorScheme="orange">4</Badge>
                      <Text fontSize="sm"><strong>Evidence Extraction:</strong> Find supporting quotes and examples</Text>
                    </HStack>
                    <HStack>
                      <Badge colorScheme="red">5</Badge>
                      <Text fontSize="sm"><strong>Recommendations:</strong> Generate actionable insights</Text>
                    </HStack>
                  </VStack>
                </VStack>
              </Box>

              <Divider />

              <Alert status="warning">
                <AlertIcon />
                <Box>
                  <Text fontSize="sm">
                    <strong>Privacy Notice:</strong> All analysis is performed locally and data is not stored externally. 
                    For production use, ensure compliance with your organization's data privacy policies.
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

      {/* Analysis History Modal */}
      <Modal isOpen={isHistoryOpen} onClose={onHistoryClose} size="xl">
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>Analysis History</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <VStack spacing={3} align="stretch">
              {analysisHistory.length === 0 ? (
                <Text color="gray.500" textAlign="center" py={8}>
                  No analysis history available
                </Text>
              ) : (
                analysisHistory.map((analysis, index) => (
                  <Card key={index} size="sm" variant="outline">
                    <CardBody>
                      <HStack justify="space-between">
                        <VStack align="start" spacing={1}>
                          <Text fontSize="sm" fontWeight="semibold">
                            {analysis.total_tickets} tickets analyzed
                          </Text>
                          <Text fontSize="xs" color="gray.600" noOfLines={2}>
                            {analysis.root_cause_statement}
                          </Text>
                          <Badge 
                            colorScheme={getConfidenceColor(analysis.confidence_score)}
                            variant="subtle"
                            fontSize="xs"
                          >
                            {(analysis.confidence_score * 100).toFixed(1)}% confidence
                          </Badge>
                        </VStack>
                        <Text fontSize="xs" color="gray.500">
                          {new Date(analysis.created_at).toLocaleString()}
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

export default UnstructuredDataSummarizer;