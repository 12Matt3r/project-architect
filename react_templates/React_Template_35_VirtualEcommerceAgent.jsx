/**
 * Template #35: Virtual E-Commerce Agent - React Frontend
 * 
 * AI-powered e-commerce platform with ReAct cycle visualization.
 * Displays the complete Thought → Action → Observation → Answer workflow.
 * 
 * Author: MiniMax Agent
 * Date: 2025-11-17
 */

import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  VStack,
  HStack,
  Text,
  Button,
  Input,
  Textarea,
  Card,
  CardBody,
  CardHeader,
  Heading,
  Flex,
  Badge,
  Avatar,
  AvatarGroup,
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
  Image,
  AspectRatio
} from '@chakra-ui/react';
import {
  FiSearch,
  FiBrain,
  FiFilter,
  FiEye,
  FiCheckCircle,
  FiShoppingCart,
  FiStar,
  FiDollarSign,
  FiLayers,
  FiTrendingUp,
  FiMessageSquare,
  FiHistory,
  FiRefreshCw,
  FiMaximize2,
  FiMinimize2,
  FiShare2,
  FiHeart
} from 'react-icons/fi';

// API Configuration
const API_BASE_URL = 'http://localhost:8000/api/v1';

// Types and Interfaces
interface Product {
  id: string;
  name: string;
  category: string;
  brand: string;
  price: number;
  description: string;
  features: string[];
  specifications: Record<string, any>;
  ratings: number;
  review_count: number;
  image_url: string;
  in_stock: boolean;
  tags: string[];
}

interface ReActStep {
  step_type: string;
  content: string;
  timestamp: string;
  metadata?: Record<string, any>;
}

interface ReActCycle {
  query: string;
  steps: ReActStep[];
  final_recommendation: string;
  confidence_score: number;
  session_id: string;
  timestamp: string;
}

interface ProductRecommendation {
  product: Product;
  match_score: number;
  reasoning: string;
  key_features: string[];
}

interface QueryResponse {
  session_id: string;
  react_cycle: ReActCycle;
  recommendations: ProductRecommendation[];
  analysis_summary: string;
}

// Main Component
const VirtualEcommerceAgent: React.FC = () => {
  // State Management
  const [query, setQuery] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [currentResponse, setCurrentResponse] = useState<QueryResponse | null>(null);
  const [sessionHistory, setSessionHistory] = useState<any[]>([]);
  const [catalog, setCatalog] = useState<any>(null);
  const [activeStep, setActiveStep] = useState<number>(-1);
  const [isComparisonMode, setIsComparisonMode] = useState(false);
  const [selectedProducts, setSelectedProducts] = useState<string[]>([]);
  const [fullscreenStep, setFullscreenStep] = useState<number | null>(null);
  
  // Hooks
  const toast = useToast();
  const { isOpen, onOpen, onClose } = useDisclosure();
  const { isOpen: isHistoryOpen, onOpen: onHistoryOpen, onClose: onHistoryClose } = useDisclosure();

  // Load initial data
  useEffect(() => {
    loadCatalog();
    loadSessionHistory();
  }, []);

  // API Functions
  const loadCatalog = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/catalog`);
      const data = await response.json();
      setCatalog(data);
    } catch (error) {
      toast({
        title: 'Error loading catalog',
        description: 'Failed to load product catalog',
        status: 'error',
        duration: 5000,
        isClosable: true
      });
    }
  };

  const loadSessionHistory = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/sessions/history?limit=20`);
      const data = await response.json();
      setSessionHistory(data.sessions || []);
    } catch (error) {
      console.error('Failed to load session history:', error);
    }
  };

  const processQuery = async () => {
    if (!query.trim()) {
      toast({
        title: 'Query Required',
        description: 'Please enter a product query',
        status: 'warning',
        duration: 3000,
        isClosable: true
      });
      return;
    }

    setIsProcessing(true);
    setActiveStep(-1);

    try {
      const response = await fetch(`${API_BASE_URL}/query`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query }),
      });

      if (!response.ok) {
        throw new Error('Failed to process query');
      }

      const data: QueryResponse = await response.json();
      setCurrentResponse(data);
      setActiveStep(0); // Start with first step
      loadSessionHistory(); // Refresh history

      toast({
        title: 'Query Processed',
        description: 'ReAct cycle completed successfully',
        status: 'success',
        duration: 3000,
        isClosable: true
      });

    } catch (error) {
      toast({
        title: 'Processing Error',
        description: 'Failed to process your query. Please try again.',
        status: 'error',
        duration: 5000,
        isClosable: true
      });
    } finally {
      setIsProcessing(false);
    }
  };

  // ReAct Step Visualization Component
  const ReActStepCard: React.FC<{ step: ReActStep; index: number; isActive: boolean; isFullscreen?: boolean }> = ({ 
    step, 
    index, 
    isActive, 
    isFullscreen = false 
  }) => {
    const getStepIcon = (stepType: string) => {
      switch (stepType.toLowerCase()) {
        case 'thought':
          return <FiBrain />;
        case 'action':
          return <FiFilter />;
        case 'observation':
          return <FiEye />;
        case 'answer':
          return <FiCheckCircle />;
        default:
          return <FiMessageSquare />;
      }
    };

    const getStepColor = (stepType: string) => {
      switch (stepType.toLowerCase()) {
        case 'thought':
          return 'blue';
        case 'action':
          return 'orange';
        case 'observation':
          return 'purple';
        case 'answer':
          return 'green';
        default:
          return 'gray';
      }
    };

    const stepColor = getStepColor(step.step_type);

    return (
      <Card 
        borderWidth={isActive ? 3 : 1}
        borderColor={`${stepColor}.400`}
        bg={isActive ? `${stepColor}.50` : 'white'}
        transition="all 0.3s ease"
        cursor="pointer"
        onClick={() => !isFullscreen && setFullscreenStep(index)}
        position="relative"
      >
        <CardHeader pb={2}>
          <HStack justify="space-between" align="center">
            <HStack>
              <Box
                p={2}
                borderRadius="full"
                bg={`${stepColor}.100`}
                color={`${stepColor}.600`}
              >
                {getStepIcon(step.step_type)}
              </Box>
              <VStack align="start" spacing={0}>
                <Heading size="sm" color={`${stepColor}.700`}>
                  Step {index + 1}: {step.step_type}
                </Heading>
                <Text fontSize="xs" color="gray.500">
                  {new Date(step.timestamp).toLocaleTimeString()}
                </Text>
              </VStack>
            </HStack>
            {isActive && (
              <Badge colorScheme={stepColor} variant="solid">
                Active
              </Badge>
            )}
          </HStack>
        </CardHeader>
        
        <CardBody pt={0}>
          <Text 
            fontSize={isFullscreen ? "md" : "sm"} 
            lineHeight={isFullscreen ? "1.6" : "1.4"}
            noOfLines={isFullscreen ? undefined : 3}
          >
            {step.content}
          </Text>
          
          {step.metadata && Object.keys(step.metadata).length > 0 && (
            <Box mt={3}>
              <Accordion size="sm" allowToggle>
                <AccordionItem border="none">
                  <AccordionButton px={0}>
                    <Text fontSize="xs" fontWeight="semibold" color="gray.600">
                      View Details
                    </Text>
                    <AccordionIcon />
                  </AccordionButton>
                  <AccordionPanel pb={0}>
                    <Box 
                      p={2} 
                      bg="gray.50" 
                      borderRadius="md" 
                      fontSize="xs"
                      maxH="200px"
                      overflowY="auto"
                    >
                      <pre style={{ whiteSpace: 'pre-wrap' }}>
                        {JSON.stringify(step.metadata, null, 2)}
                      </pre>
                    </Box>
                  </AccordionPanel>
                </AccordionItem>
              </Accordion>
            </Box>
          )}
        </CardBody>
      </Card>
    );
  };

  // Product Recommendation Card Component
  const ProductRecommendationCard: React.FC<{ 
    recommendation: ProductRecommendation; 
    rank: number;
    isSelected?: boolean;
    onSelect?: () => void;
  }> = ({ recommendation, rank, isSelected = false, onSelect }) => {
    const { product, match_score, reasoning, key_features } = recommendation;

    return (
      <Card 
        borderWidth={isSelected ? 2 : 1}
        borderColor={isSelected ? 'blue.400' : 'gray.200'}
        transition="all 0.3s ease"
        _hover={{ shadow: 'lg', transform: 'translateY(-2px)' }}
      >
        <CardHeader pb={2}>
          <HStack justify="space-between" align="start">
            <HStack>
              <Box
                p={2}
                borderRadius="full"
                bg={rank === 1 ? 'gold.100' : rank === 2 ? 'silver.100' : 'bronze.100'}
                color={rank === 1 ? 'gold.600' : rank === 2 ? 'silver.600' : 'bronze.600'}
                fontWeight="bold"
                minW="40px"
                textAlign="center"
              >
                #{rank}
              </Box>
              <VStack align="start" spacing={1}>
                <Heading size="sm">{product.name}</Heading>
                <HStack>
                  <Text fontSize="sm" color="gray.600">{product.brand}</Text>
                  <Badge colorScheme="blue" size="sm">{product.category}</Badge>
                </HStack>
              </VStack>
            </HStack>
            <VStack align="end" spacing={1}>
              <Text fontSize="lg" fontWeight="bold" color="green.600">
                ${product.price.toFixed(2)}
              </Text>
              <HStack>
                <FiStar color="gold" />
                <Text fontSize="sm">{product.ratings}</Text>
                <Text fontSize="xs" color="gray.500">({product.review_count})</Text>
              </HStack>
            </VStack>
          </HStack>
        </CardHeader>

        <CardBody pt={0}>
          <VStack align="stretch" spacing={3}>
            <Box>
              <HStack justify="space-between" mb={2}>
                <Text fontSize="sm" fontWeight="semibold">Match Score</Text>
                <Text fontSize="sm" fontWeight="bold" color="blue.600">
                  {match_score.toFixed(1)}%
                </Text>
              </HStack>
              <Progress 
                value={match_score} 
                colorScheme={match_score >= 80 ? 'green' : match_score >= 60 ? 'yellow' : 'red'}
                size="sm"
                borderRadius="md"
              />
            </Box>

            <Box>
              <Text fontSize="sm" fontWeight="semibold" mb={1}>Why this product:</Text>
              <Text fontSize="sm" color="gray.700">{reasoning}</Text>
            </Box>

            <Box>
              <Text fontSize="sm" fontWeight="semibold" mb={2}>Key Features:</Text>
              <Wrap>
                {key_features.map((feature, index) => (
                  <WrapItem key={index}>
                    <Badge colorScheme="purple" variant="subtle" fontSize="xs">
                      {feature}
                    </Badge>
                  </WrapItem>
                ))}
              </Wrap>
            </Box>

            <AspectRatio ratio={16/9} borderRadius="md" overflow="hidden">
              <Image 
                src={product.image_url} 
                alt={product.name}
                objectFit="cover"
                fallbackSrc="https://via.placeholder.com/400x225?text=Product+Image"
              />
            </AspectRatio>

            <HStack justify="space-between">
              <Button
                size="sm"
                colorScheme="blue"
                leftIcon={<FiShoppingCart />}
                onClick={() => toast({
                  title: 'Added to Cart',
                  description: `${product.name} added to cart`,
                  status: 'success',
                  duration: 2000
                })}
              >
                Add to Cart
              </Button>
              <HStack>
                <Tooltip label="Add to Wishlist">
                  <IconButton
                    size="sm"
                    variant="outline"
                    icon={<FiHeart />}
                    aria-label="Add to wishlist"
                  />
                </Tooltip>
                <Tooltip label="Compare">
                  <IconButton
                    size="sm"
                    variant="outline"
                    icon={<FiLayers />}
                    aria-label="Compare product"
                    colorScheme={isSelected ? 'blue' : 'gray'}
                    onClick={onSelect}
                  />
                </Tooltip>
              </HStack>
            </HStack>
          </VStack>
        </CardBody>
      </Card>
    );
  };

  // Sample Queries Component
  const SampleQueries: React.FC<{ onSelect: (query: string) => void }> = ({ onSelect }) => {
    const sampleQueries = [
      "What's the best running shoe for a marathon runner with high arches?",
      "I need comfortable casual shoes for daily wear under $150",
      "Looking for basketball shoes with excellent ankle support",
      "What running shoes are best for trail running?",
      "I need arch support shoes for someone with flat feet",
      "Show me lightweight racing shoes for track events"
    ];

    return (
      <Card>
        <CardHeader>
          <Heading size="sm">Try These Sample Queries</Heading>
        </CardHeader>
        <CardBody pt={0}>
          <VStack align="stretch" spacing={2}>
            {sampleQueries.map((sampleQuery, index) => (
              <Button
                key={index}
                size="sm"
                variant="ghost"
                justifyContent="flex-start"
                textAlign="left"
                onClick={() => onSelect(sampleQuery)}
                _hover={{ bg: 'gray.50' }}
              >
                <Text fontSize="sm" color="blue.600">{sampleQuery}</Text>
              </Button>
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
                  <Heading size="lg">Virtual E-Commerce Agent</Heading>
                  <Text color="gray.600">
                    AI-powered shopping assistant using ReAct methodology
                  </Text>
                </VStack>
                <HStack>
                  <Button
                    leftIcon={<FiHistory />}
                    variant="outline"
                    size="sm"
                    onClick={onHistoryOpen}
                  >
                    History
                  </Button>
                  <Button
                    leftIcon={<FiRefreshCw />}
                    variant="ghost"
                    size="sm"
                    onClick={loadCatalog}
                  >
                    Refresh Catalog
                  </Button>
                </HStack>
              </HStack>

              <Box w="full">
                <HStack spacing={4}>
                  <Input
                    placeholder="Ask about any product (e.g., 'What's the best running shoe for marathon with high arches?')"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    size="lg"
                    flex={1}
                    onKeyPress={(e) => e.key === 'Enter' && !isProcessing && processQuery()}
                  />
                  <Button
                    leftIcon={isProcessing ? <Spinner size="sm" /> : <FiSearch />}
                    colorScheme="blue"
                    size="lg"
                    onClick={processQuery}
                    isLoading={isProcessing}
                    loadingText="Processing..."
                  >
                    Search
                  </Button>
                </HStack>
              </Box>
            </VStack>
          </CardBody>
        </Card>

        {/* Main Content Area */}
        <Grid templateColumns={{ base: '1fr', lg: '1fr 400px' }} gap={6}>
          {/* Left Column: ReAct Cycle and Results */}
          <VStack spacing={6} align="stretch">
            
            {/* ReAct Cycle Visualization */}
            {currentResponse && (
              <Card>
                <CardHeader>
                  <HStack justify="space-between">
                    <VStack align="start" spacing={1}>
                      <Heading size="md">ReAct Cycle Analysis</Heading>
                      <Text fontSize="sm" color="gray.600">
                        Session: {currentResponse.session_id.substring(0, 8)}...
                      </Text>
                    </VStack>
                    <Badge 
                      colorScheme="green" 
                      fontSize="sm" 
                      px={3} 
                      py={1}
                    >
                      Confidence: {currentResponse.react_cycle.confidence_score.toFixed(1)}%
                    </Badge>
                  </HStack>
                </CardHeader>
                <CardBody pt={0}>
                  <VStack 
                    spacing={4} 
                    align="stretch"
                    divider={<StackDivider borderColor="gray.200" />}
                  >
                    {currentResponse.react_cycle.steps.map((step, index) => (
                      <ReActStepCard
                        key={index}
                        step={step}
                        index={index}
                        isActive={activeStep === index}
                      />
                    ))}
                  </VStack>
                </CardBody>
              </Card>
            )}

            {/* Product Recommendations */}
            {currentResponse && currentResponse.recommendations.length > 0 && (
              <Card>
                <CardHeader>
                  <HStack justify="space-between">
                    <VStack align="start" spacing={1}>
                      <Heading size="md">Top Recommendations</Heading>
                      <Text fontSize="sm" color="gray.600">
                        AI-selected products based on your query
                      </Text>
                    </VStack>
                    <Button
                      size="sm"
                      variant="outline"
                      leftIcon={<FiLayers />}
                      onClick={() => setIsComparisonMode(!isComparisonMode)}
                      colorScheme={isComparisonMode ? 'blue' : 'gray'}
                    >
                      {isComparisonMode ? 'Exit Comparison' : 'Compare Selected'}
                    </Button>
                  </HStack>
                </CardHeader>
                <CardBody pt={0}>
                  <Grid templateColumns={{ base: '1fr', md: 'repeat(2, 1fr)' }} gap={4}>
                    {currentResponse.recommendations.map((recommendation, index) => (
                      <ProductRecommendationCard
                        key={recommendation.product.id}
                        recommendation={recommendation}
                        rank={index + 1}
                        isSelected={selectedProducts.includes(recommendation.product.id)}
                        onSelect={() => {
                          setSelectedProducts(prev => 
                            prev.includes(recommendation.product.id)
                              ? prev.filter(id => id !== recommendation.product.id)
                              : [...prev, recommendation.product.id]
                          );
                        }}
                      />
                    ))}
                  </Grid>

                  {isComparisonMode && selectedProducts.length > 0 && (
                    <Box mt={4} p={4} bg="blue.50" borderRadius="md">
                      <HStack justify="space-between" mb={3}>
                        <Text fontSize="sm" fontWeight="semibold">
                          Selected for Comparison: {selectedProducts.length}
                        </Text>
                        <Button
                          size="sm"
                          colorScheme="blue"
                          isDisabled={selectedProducts.length < 2}
                          onClick={() => toast({
                            title: 'Feature Coming Soon',
                            description: 'Product comparison feature will be available in the next update',
                            status: 'info',
                            duration: 3000
                          })}
                        >
                          Compare Now
                        </Button>
                      </HStack>
                      <Wrap>
                        {selectedProducts.map(productId => {
                          const product = currentResponse.recommendations
                            .find(r => r.product.id === productId)?.product;
                          return product ? (
                            <WrapItem key={productId}>
                              <Badge colorScheme="blue" variant="outline">
                                {product.name}
                              </Badge>
                            </WrapItem>
                          ) : null;
                        })}
                      </Wrap>
                    </Box>
                  )}
                </CardBody>
              </Card>
            )}

            {/* Analysis Summary */}
            {currentResponse && (
              <Card>
                <CardHeader>
                  <Heading size="md">Analysis Summary</Heading>
                </CardHeader>
                <CardBody pt={0}>
                  <Text 
                    whiteSpace="pre-wrap" 
                    fontSize="sm" 
                    lineHeight="1.6"
                    color="gray.700"
                  >
                    {currentResponse.analysis_summary}
                  </Text>
                </CardBody>
              </Card>
            )}

            {/* Processing Indicator */}
            {isProcessing && (
              <Card>
                <CardBody>
                  <VStack spacing={4}>
                    <Spinner size="xl" color="blue.500" />
                    <Text fontWeight="semibold">Processing your query through ReAct cycle...</Text>
                    <Text fontSize="sm" color="gray.600" textAlign="center">
                      Our AI is analyzing your needs, filtering our catalog, 
                      and generating personalized recommendations.
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
            
            {/* Sample Queries */}
            <SampleQueries onSelect={setQuery} />

            {/* Catalog Overview */}
            {catalog && (
              <Card>
                <CardHeader>
                  <Heading size="sm">Catalog Overview</Heading>
                </CardHeader>
                <CardBody pt={0}>
                  <VStack spacing={3} align="stretch">
                    <Box>
                      <HStack justify="space-between">
                        <Text fontSize="sm">Total Products</Text>
                        <Text fontSize="sm" fontWeight="bold">{catalog.total_products}</Text>
                      </HStack>
                    </Box>
                    <Divider />
                    {Object.entries(catalog.catalog).map(([category, info]: [string, any]) => (
                      <Box key={category}>
                        <HStack justify="space-between" mb={1}>
                          <Text fontSize="sm" fontWeight="semibold" textTransform="capitalize">
                            {category.replace('_', ' ')}
                          </Text>
                          <Badge colorScheme="blue" size="sm">
                            {info.count}
                          </Badge>
                        </HStack>
                        <Text fontSize="xs" color="gray.600">
                          {info.brands.length} brands
                        </Text>
                        <Text fontSize="xs" color="gray.600">
                          ${info.price_range.min} - ${info.price_range.max}
                        </Text>
                      </Box>
                    ))}
                  </VStack>
                </CardBody>
              </Card>
            )}

            {/* ReAct Methodology Info */}
            <Card>
              <CardHeader>
                <Heading size="sm">ReAct Methodology</Heading>
              </CardHeader>
              <CardBody pt={0}>
                <VStack spacing={3} align="stretch">
                  <Text fontSize="xs" color="gray.600">
                    Our AI uses the ReAct (Reasoning and Acting) framework to provide intelligent recommendations:
                  </Text>
                  
                  <VStack spacing={2} align="stretch" pl={2}>
                    <HStack>
                      <Box w={3} h={3} bg="blue.400" borderRadius="full" />
                      <Text fontSize="xs"><strong>Thought:</strong> Analyze your needs</Text>
                    </HStack>
                    <HStack>
                      <Box w={3} h={3} bg="orange.400" borderRadius="full" />
                      <Text fontSize="xs"><strong>Action:</strong> Filter catalog</Text>
                    </HStack>
                    <HStack>
                      <Box w={3} h={3} bg="purple.400" borderRadius="full" />
                      <Text fontSize="xs"><strong>Observation:</strong> Review results</Text>
                    </HStack>
                    <HStack>
                      <Box w={3} h={3} bg="green.400" borderRadius="full" />
                      <Text fontSize="xs"><strong>Answer:</strong> Provide recommendation</Text>
                    </HStack>
                  </VStack>
                </VStack>
              </CardBody>
            </Card>
          </VStack>
        </Grid>
      </VStack>

      {/* Session History Modal */}
      <Modal isOpen={isHistoryOpen} onClose={onHistoryClose} size="xl">
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>Session History</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <VStack spacing={3} align="stretch">
              {sessionHistory.length === 0 ? (
                <Text color="gray.500" textAlign="center" py={8}>
                  No session history available
                </Text>
              ) : (
                sessionHistory.map((session, index) => (
                  <Card key={index} size="sm" variant="outline">
                    <CardBody>
                      <HStack justify="space-between">
                        <VStack align="start" spacing={1}>
                          <Text fontSize="sm" fontWeight="semibold" noOfLines={2}>
                            {session.query}
                          </Text>
                          <Text fontSize="xs" color="gray.500">
                            {new Date(session.timestamp).toLocaleString()}
                          </Text>
                        </VStack>
                        <Text fontSize="xs" color="gray.500">
                          {session.session_id.substring(0, 8)}...
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

      {/* Fullscreen Step Modal */}
      {fullscreenStep !== null && currentResponse && (
        <Modal isOpen={true} onClose={() => setFullscreenStep(null)} size="4xl">
          <ModalOverlay />
          <ModalContent maxH="90vh">
            <ModalHeader>
              ReAct Step {fullscreenStep + 1}: {currentResponse.react_cycle.steps[fullscreenStep].step_type}
            </ModalHeader>
            <ModalCloseButton />
            <ModalBody>
              <ReActStepCard
                step={currentResponse.react_cycle.steps[fullscreenStep]}
                index={fullscreenStep}
                isActive={true}
                isFullscreen={true}
              />
            </ModalBody>
            <ModalFooter>
              <Button onClick={() => setFullscreenStep(null)}>
                Close
              </Button>
            </ModalFooter>
          </ModalContent>
        </Modal>
      )}
    </Box>
  );
};

export default VirtualEcommerceAgent;