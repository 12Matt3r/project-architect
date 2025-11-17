/**
 * Template #29: Dynamic API Documenter - React Frontend
 * Advanced AI-powered OpenAPI specification analysis and v2.0 enhancement generation interface
 * 
 * Author: MiniMax Agent
 * Date: 2025-11-17
 */

import React, { useState, useCallback } from 'react';
import {
  Box,
  Container,
  VStack,
  HStack,
  Heading,
  Text,
  Button,
  Card,
  CardBody,
  CardHeader,
  Grid,
  GridItem,
  Badge,
  Progress,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  Spinner,
  useToast,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
  Flex,
  Icon,
  Divider,
  useColorModeValue,
  Tooltip,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalFooter,
  ModalBody,
  ModalCloseButton,
  useDisclosure,
  Tag,
  TagLabel,
  Wrap,
  WrapItem,
  IconButton,
  Select,
  Input,
  Textarea,
  Code,
  CodeBlock,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  StatArrow,
  Switch,
  FormControl,
  FormLabel,
  NumberInput,
  NumberInputField,
  NumberInputStepper,
  NumberIncrementStepper,
  NumberDecrementStepper
} from '@chakra-ui/react';
import {
  FaUpload,
  FaFileCode,
  FaChartLine,
  FaDownload,
  FaShare,
  FaFilter,
  FaSearch,
  FaRobot,
  FaBrain,
  FaEye,
  FaEdit,
  FaCog,
  FaExclamationTriangle,
  FaCheckCircle,
  FaTimesCircle,
  FaInfoCircle,
  FaFileAlt,
  FaCode,
  FaMagic,
  FaSync,
  FaSave,
  FaClipboard,
  FaExpand,
  FaCompress,
  FaHistory,
  FaExpandArrowsAlt,
  FaCompressArrowsAlt
} from 'react-icons/fa';

// Color mode values
const bgColor = useColorModeValue('gray.50', 'gray.900');
const cardBg = useColorModeValue('white', 'gray.800');
const borderColor = useColorModeValue('gray.200', 'gray.600');
const highlightColor = useColorModeValue('blue.50', 'blue.900');

// Types
interface Weakness {
  category: string;
  severity: string;
  description: string;
  impact: string;
  recommendation: string;
}

interface Enhancement {
  type: string;
  description: string;
  files_affected: string;
}

interface EnhancedSpec {
  spec_id: string;
  enhanced_openapi: any;
  weaknesses_identified: Weakness[];
  enhancements_made: Enhancement[];
  improvements_by_endpoint: any[];
  timestamp: string;
}

// Mock data for demonstration
const mockSpec = {
  "openapi": "3.0.0",
  "info": {
    "title": "Sample API",
    "version": "1.0.0",
    "description": "A sample API for demonstration"
  },
  "paths": {
    "/users": {
      "get": {
        "summary": "Get users",
        "description": "Retrieve all users",
        "responses": {
          "200": {
            "description": "Success"
          }
        }
      }
    }
  }
};

const mockWeaknesses: Weakness[] = [
  {
    category: "Documentation",
    severity: "High",
    description: "Low documentation quality score (45.2%)",
    impact: "Developers will struggle to understand and use the API effectively",
    recommendation: "Improve endpoint descriptions, add examples, and document parameters clearly"
  },
  {
    category: "Security",
    severity: "High",
    description: "Insufficient security configuration (score: 35%)",
    impact: "API may be vulnerable to unauthorized access and security breaches",
    recommendation: "Implement proper authentication, authorization, and security schemes"
  },
  {
    category: "Performance",
    severity: "Medium",
    description: "List endpoints missing pagination",
    impact: "Large datasets will cause performance issues and timeout errors",
    recommendation: "Implement pagination parameters for all list endpoints"
  }
];

const mockEnhancements: Enhancement[] = [
  {
    type: "Documentation Enhancement",
    description: "Improved endpoint descriptions and parameter documentation",
    files_affected: "All endpoints"
  },
  {
    type: "Security Enhancement",
    description: "Added comprehensive security schemes and requirements",
    files_affected: "Global security configuration"
  },
  {
    type: "Performance Enhancement",
    description: "Added pagination support for list endpoints",
    files_affected: "List endpoints"
  },
  {
    type: "Schema Enhancement",
    description: "Added examples to all schemas and endpoints",
    files_affected: "All schemas and endpoints"
  }
];

const App: React.FC = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [specContent, setSpecContent] = useState<string>('');
  const [specFormat, setSpecFormat] = useState<string>('json');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<EnhancedSpec | null>(null);
  const [showComparison, setShowComparison] = useState(false);
  const [viewMode, setViewMode] = useState<'raw' | 'formatted'>('formatted');
  const [filterSeverity, setFilterSeverity] = useState<string>('all');
  const [searchTerm, setSearchTerm] = useState('');
  const { isOpen, onOpen, onClose } = useDisclosure();
  const [expandedSection, setExpandedSection] = useState<string | null>(null);
  const toast = useToast();

  // Event handlers
  const handleFileSelect = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      // Validate file type
      if (!file.name.endsWith('.json') && !file.name.endsWith('.yaml') && !file.name.endsWith('.yml')) {
        toast({
          title: 'Invalid file type',
          description: 'Please select an OpenAPI specification file (JSON or YAML)',
          status: 'error',
          duration: 5000,
          isClosable: true,
        });
        return;
      }

      setSelectedFile(file);

      // Set format based on file extension
      const extension = file.name.split('.').pop()?.toLowerCase();
      if (extension === 'json') {
        setSpecFormat('json');
      } else {
        setSpecFormat('yaml');
      }

      // Read file content
      const reader = new FileReader();
      reader.onload = (e) => {
        setSpecContent(e.target?.result as string);
      };
      reader.readAsText(file);

      toast({
        title: 'File Loaded',
        description: `${file.name} has been loaded successfully`,
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
    }
  }, [toast]);

  const handleAnalyze = useCallback(async () => {
    if (!specContent.trim()) {
      toast({
        title: 'No specification content',
        description: 'Please upload an OpenAPI specification file',
        status: 'warning',
        duration: 5000,
        isClosable: true,
      });
      return;
    }

    setIsAnalyzing(true);

    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 4000));

      const mockResult: EnhancedSpec = {
        spec_id: `spec_${Date.now()}`,
        enhanced_openapi: mockSpec,
        weaknesses_identified: mockWeaknesses,
        enhancements_made: mockEnhancements,
        improvements_by_endpoint: [],
        timestamp: new Date().toISOString()
      };

      setAnalysisResult(mockResult);

      toast({
        title: 'Analysis Complete!',
        description: 'OpenAPI specification has been analyzed and enhanced',
        status: 'success',
        duration: 5000,
        isClosable: true,
      });

    } catch (error) {
      toast({
        title: 'Analysis Failed',
        description: 'Failed to analyze the specification. Please try again.',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setIsAnalyzing(false);
    }
  }, [specContent, toast]);

  const getSeverityColor = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'high': return 'red';
      case 'medium': return 'orange';
      case 'low': return 'yellow';
      default: return 'gray';
    }
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'high': return FaExclamationTriangle;
      case 'medium': return FaInfoCircle;
      case 'low': return FaCheckCircle;
      default: return FaInfoCircle;
    }
  };

  const filteredWeaknesses = analysisResult?.weaknesses_identified.filter(weakness => {
    const matchesFilter = filterSeverity === 'all' || 
      weakness.severity.toLowerCase() === filterSeverity.toLowerCase();
    const matchesSearch = searchTerm === '' || 
      weakness.category.toLowerCase().includes(searchTerm.toLowerCase()) ||
      weakness.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
      weakness.recommendation.toLowerCase().includes(searchTerm.toLowerCase());
    
    return matchesFilter && matchesSearch;
  }) || [];

  const downloadEnhancedSpec = () => {
    if (!analysisResult) return;
    
    const content = viewMode === 'formatted' 
      ? JSON.stringify(analysisResult.enhanced_openapi, null, 2)
      : JSON.stringify(analysisResult.enhanced_openapi);
    
    const blob = new Blob([content], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `enhanced-api-spec-v2.0.${specFormat}`;
    a.click();
    URL.revokeObjectURL(url);

    toast({
      title: 'Download Started',
      description: 'Enhanced specification is being downloaded',
      status: 'info',
      duration: 3000,
      isClosable: true,
    });
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    toast({
      title: 'Copied to Clipboard',
      description: 'Content has been copied to your clipboard',
      status: 'success',
      duration: 2000,
      isClosable: true,
    });
  };

  return (
    <Box bg={bgColor} minH="100vh">
      <Container maxW="7xl" py={8}>
        {/* Header */}
        <VStack spacing={6} align="stretch">
          <Box textAlign="center">
            <HStack justify="center" spacing={4} mb={4}>
              <Icon as={FaFileCode} boxSize={8} color="blue.500" />
              <Heading size="2xl" bgGradient="linear(to-r, blue.400, purple.500)" bgClip="text">
                Dynamic API Documenter
              </Heading>
              <Icon as={FaBrain} boxSize={8} color="purple.500" />
            </HStack>
            <Text fontSize="xl" color="gray.600">
              AI-powered OpenAPI specification analysis and v2.0 enhancement generation
            </Text>
          </Box>

          {/* Upload Section */}
          <Card bg={cardBg} borderWidth="1px" borderColor={borderColor}>
            <CardHeader>
              <HStack>
                <Icon as={FaUpload} color="blue.500" />
                <Heading size="md">Upload OpenAPI Specification</Heading>
              </HStack>
            </CardHeader>
            <CardBody>
              <VStack spacing={4}>
                <Box
                  borderWidth="2px"
                  borderStyle="dashed"
                  borderColor="gray.300"
                  borderRadius="lg"
                  p={8}
                  textAlign="center"
                  w="full"
                  transition="all 0.3s"
                  _hover={{
                    borderColor: 'blue.400',
                    bg: 'blue.50'
                  }}
                >
                  <Input
                    type="file"
                    accept=".json,.yaml,.yml"
                    onChange={handleFileSelect}
                    display="none"
                    id="file-upload"
                  />
                  <label htmlFor="file-upload" style={{ cursor: 'pointer' }}>
                    <VStack spacing={4}>
                      <Icon as={FaFileAlt} boxSize={12} color="gray.400" />
                      <Text fontSize="lg" fontWeight="medium">
                        Click to upload OpenAPI specification
                      </Text>
                      <Text fontSize="sm" color="gray.500">
                        JSON or YAML files up to 5MB
                      </Text>
                      <Button colorScheme="blue" leftIcon={<FaUpload />}>
                        Choose File
                      </Button>
                    </VStack>
                  </label>
                </Box>

                {selectedFile && (
                  <Box w="full">
                    <Text fontWeight="medium" mb={2}>Selected File:</Text>
                    <HStack justify="space-between" p={3} bg={highlightColor} borderRadius="md">
                      <HStack>
                        <Icon as={FaFileCode} color="blue.500" />
                        <VStack align="start" spacing={0}>
                          <Text fontWeight="medium">{selectedFile.name}</Text>
                          <Text fontSize="sm" color="gray.600">
                            {(selectedFile.size / 1024).toFixed(1)} KB • {specFormat.toUpperCase()}
                          </Text>
                        </VStack>
                      </HStack>
                      <IconButton
                        aria-label="Remove file"
                        icon={<FaTimesCircle />}
                        size="sm"
                        variant="ghost"
                        onClick={() => {
                          setSelectedFile(null);
                          setSpecContent('');
                        }}
                      />
                    </HStack>
                  </Box>
                )}

                <Button
                  colorScheme="blue"
                  size="lg"
                  leftIcon={isAnalyzing ? <Spinner size="sm" /> : <FaMagic />}
                  onClick={handleAnalyze}
                  isLoading={isAnalyzing}
                  loadingText="Analyzing Specification..."
                  isDisabled={!specContent.trim()}
                >
                  Analyze & Enhance API
                </Button>
              </VStack>
            </CardBody>
          </Card>

          {/* Results Section */}
          {analysisResult && (
            <VStack spacing={6} align="stretch">
              {/* Analysis Overview */}
              <Card bg={cardBg} borderWidth="1px" borderColor={borderColor}>
                <CardHeader>
                  <HStack justify="space-between">
                    <HStack>
                      <Icon as={FaChartLine} color="green.500" />
                      <Heading size="md">Analysis Overview</Heading>
                    </HStack>
                    <HStack>
                      <FormControl display="flex" alignItems="center">
                        <FormLabel htmlFor="comparison-toggle" mb="0" fontSize="sm">
                          Side-by-side comparison
                        </FormLabel>
                        <Switch
                          id="comparison-toggle"
                          isChecked={showComparison}
                          onChange={(e) => setShowComparison(e.target.checked)}
                        />
                      </FormControl>
                      <Button
                        leftIcon={<FaDownload />}
                        colorScheme="green"
                        variant="outline"
                        size="sm"
                        onClick={downloadEnhancedSpec}
                      >
                        Download v2.0
                      </Button>
                    </HStack>
                  </HStack>
                </CardHeader>
                <CardBody>
                  <Grid templateColumns="repeat(auto-fit, minmax(200px, 1fr))" gap={6}>
                    <Stat>
                      <StatLabel>Weaknesses Identified</StatLabel>
                      <StatNumber color="red.500">{analysisResult.weaknesses_identified.length}</StatNumber>
                      <StatHelpText>
                        <Icon as={FaExclamationTriangle} mr={1} />
                        Require attention
                      </StatHelpText>
                    </Stat>
                    <Stat>
                      <StatLabel>Enhancements Applied</StatLabel>
                      <StatNumber color="blue.500">{analysisResult.enhancements_made.length}</StatNumber>
                      <StatHelpText>
                        <Icon as={FaMagic} mr={1} />
                        Performance improvements
                      </StatHelpText>
                    </Stat>
                    <Stat>
                      <StatLabel>API Version</StatLabel>
                      <StatNumber>2.0.0</StatNumber>
                      <StatHelpText>
                        <Icon as={FaSync} mr={1} />
                        Enhanced specification
                      </StatHelpText>
                    </Stat>
                    <Stat>
                      <StatLabel>Analysis ID</StatLabel>
                      <StatNumber fontSize="md" fontFamily="mono">
                        {analysisResult.spec_id.slice(0, 8)}...
                      </StatNumber>
                      <StatHelpText>
                        <Icon as={FaHistory} mr={1} />
                        {new Date(analysisResult.timestamp).toLocaleString()}
                      </StatHelpText>
                    </Stat>
                  </Grid>
                </CardBody>
              </Card>

              {/* Main Content Tabs */}
              <Card bg={cardBg} borderWidth="1px" borderColor={borderColor}>
                <CardBody>
                  <Tabs variant="enclosed">
                    <TabList>
                      <Tab><Icon as={FaExclamationTriangle} mr={2} />Weaknesses Analysis</Tab>
                      <Tab><Icon as={FaMagic} mr={2} />Enhancements</Tab>
                      <Tab><Icon as={FaFileCode} mr={2} />Enhanced Specification</Tab>
                      <Tab><Icon as={FaEye} mr={2} />Preview</Tab>
                    </TabList>

                    <TabPanels>
                      {/* Weaknesses Tab */}
                      <TabPanel>
                        <VStack align="stretch" spacing={4}>
                          {/* Filters */}
                          <HStack spacing={4} flexWrap="wrap">
                            <Box>
                              <Text fontSize="sm" fontWeight="medium" mb={1}>Filter by Severity:</Text>
                              <Select
                                value={filterSeverity}
                                onChange={(e) => setFilterSeverity(e.target.value)}
                                size="sm"
                                w="150px"
                              >
                                <option value="all">All Severities</option>
                                <option value="high">High</option>
                                <option value="medium">Medium</option>
                                <option value="low">Low</option>
                              </Select>
                            </Box>
                            <Box>
                              <Text fontSize="sm" fontWeight="medium" mb={1}>Search Issues:</Text>
                              <Input
                                placeholder="Search weaknesses..."
                                value={searchTerm}
                                onChange={(e) => setSearchTerm(e.target.value)}
                                size="sm"
                                w="250px"
                                leftElement={<Icon as={FaSearch} color="gray.400" />}
                              />
                            </Box>
                          </HStack>

                          {/* Weakness Cards */}
                          {filteredWeaknesses.map((weakness, index) => {
                            const SeverityIcon = getSeverityIcon(weakness.severity);
                            return (
                              <Card
                                key={index}
                                bg={cardBg}
                                borderWidth="1px"
                                borderColor={`${getSeverityColor(weakness.severity)}.300`}
                                borderLeftWidth="4px"
                              >
                                <CardBody>
                                  <VStack align="stretch" spacing={3}>
                                    <HStack justify="space-between">
                                      <HStack>
                                        <Icon as={SeverityIcon} color={`${getSeverityColor(weakness.severity)}.500`} />
                                        <Heading size="sm">{weakness.category}</Heading>
                                        <Badge colorScheme={getSeverityColor(weakness.severity)}>
                                          {weakness.severity}
                                        </Badge>
                                      </HStack>
                                      <IconButton
                                        aria-label="Copy details"
                                        icon={<FaClipboard />}
                                        size="sm"
                                        variant="ghost"
                                        onClick={() => copyToClipboard(JSON.stringify(weakness, null, 2))}
                                      />
                                    </HStack>
                                    
                                    <Box>
                                      <Text fontWeight="medium" mb={1}>Issue:</Text>
                                      <Text color="gray.700">{weakness.description}</Text>
                                    </Box>
                                    
                                    <Box>
                                      <Text fontWeight="medium" mb={1}>Impact:</Text>
                                      <Text color="red.600" fontSize="sm">{weakness.impact}</Text>
                                    </Box>
                                    
                                    <Box>
                                      <Text fontWeight="medium" mb={1}>Recommendation:</Text>
                                      <Text color="blue.600" fontSize="sm">{weakness.recommendation}</Text>
                                    </Box>
                                  </VStack>
                                </CardBody>
                              </Card>
                            );
                          })}

                          {filteredWeaknesses.length === 0 && (
                            <Alert status="info">
                              <AlertIcon />
                              <AlertTitle>No weaknesses match your filters</AlertTitle>
                              <AlertDescription>
                                Try adjusting your filter or search criteria to see more results.
                              </AlertDescription>
                            </Alert>
                          )}
                        </VStack>
                      </TabPanel>

                      {/* Enhancements Tab */}
                      <TabPanel>
                        <VStack align="stretch" spacing={4}>
                          {analysisResult.enhancements_made.map((enhancement, index) => (
                            <Card key={index} bg={cardBg} borderWidth="1px" borderColor="green.300">
                              <CardBody>
                                <VStack align="stretch" spacing={3}>
                                  <HStack justify="space-between">
                                    <HStack>
                                      <Icon as={FaMagic} color="green.500" />
                                      <Heading size="sm">{enhancement.type}</Heading>
                                    </HStack>
                                    <Badge colorScheme="green">Applied</Badge>
                                  </HStack>
                                  
                                  <Text>{enhancement.description}</Text>
                                  
                                  <HStack>
                                    <Icon as={FaFileCode} color="blue.500" />
                                    <Text fontSize="sm" color="gray.600">
                                      <strong>Affected:</strong> {enhancement.files_affected}
                                    </Text>
                                  </HStack>
                                </VStack>
                              </CardBody>
                            </Card>
                          ))}
                        </VStack>
                      </TabPanel>

                      {/* Enhanced Specification Tab */}
                      <TabPanel>
                        <VStack align="stretch" spacing={4}>
                          {/* Controls */}
                          <HStack justify="space-between">
                            <HStack>
                              <FormControl display="flex" alignItems="center">
                                <FormLabel htmlFor="view-mode" mb="0" fontSize="sm">
                                  View Mode:
                                </FormLabel>
                                <Select
                                  id="view-mode"
                                  value={viewMode}
                                  onChange={(e) => setViewMode(e.target.value as 'raw' | 'formatted')}
                                  size="sm"
                                  w="120px"
                                >
                                  <option value="formatted">Formatted</option>
                                  <option value="raw">Raw</option>
                                </Select>
                              </FormControl>
                            </HStack>
                            
                            <HStack>
                              <Button
                                leftIcon={<FaClipboard />}
                                size="sm"
                                variant="outline"
                                onClick={() => copyToClipboard(
                                  viewMode === 'formatted'
                                    ? JSON.stringify(analysisResult.enhanced_openapi, null, 2)
                                    : JSON.stringify(analysisResult.enhanced_openapi)
                                )}
                              >
                                Copy JSON
                              </Button>
                              <Button
                                leftIcon={<FaDownload />}
                                size="sm"
                                colorScheme="green"
                                onClick={downloadEnhancedSpec}
                              >
                                Download
                              </Button>
                            </HStack>
                          </HStack>

                          {/* Specification Display */}
                          <Box
                            bg="gray.900"
                            color="green.400"
                            p={4}
                            borderRadius="md"
                            maxH="600px"
                            overflowY="auto"
                            fontFamily="mono"
                            fontSize="sm"
                          >
                            <pre>
                              {viewMode === 'formatted'
                                ? JSON.stringify(analysisResult.enhanced_openapi, null, 2)
                                : JSON.stringify(analysisResult.enhanced_openapi)
                              }
                            </pre>
                          </Box>
                        </VStack>
                      </TabPanel>

                      {/* Preview Tab */}
                      <TabPanel>
                        <VStack align="stretch" spacing={4}>
                          {!showComparison ? (
                            <Box>
                              <HStack justify="space-between" mb={4}>
                                <Heading size="md">Enhanced Specification Preview</Heading>
                                <Text fontSize="sm" color="gray.600">
                                  Version 2.0.0
                                </Text>
                              </HStack>
                              
                              <Grid templateColumns="repeat(auto-fit, minmax(300px, 1fr))" gap={4}>
                                <Card bg={cardBg} borderWidth="1px" borderColor="green.300">
                                  <CardHeader>
                                    <Heading size="sm">API Information</Heading>
                                  </CardHeader>
                                  <CardBody>
                                    <VStack align="stretch" spacing={2}>
                                      <HStack justify="space-between">
                                        <Text fontWeight="medium">Title:</Text>
                                        <Text>{analysisResult.enhanced_openapi?.info?.title || 'API Title'}</Text>
                                      </HStack>
                                      <HStack justify="space-between">
                                        <Text fontWeight="medium">Version:</Text>
                                        <Badge colorScheme="green">{analysisResult.enhanced_openapi?.info?.version || '2.0.0'}</Badge>
                                      </HStack>
                                      <Box>
                                        <Text fontWeight="medium">Description:</Text>
                                        <Text fontSize="sm" color="gray.600">
                                          {analysisResult.enhanced_openapi?.info?.description || 'Enhanced API description'}
                                        </Text>
                                      </Box>
                                    </VStack>
                                  </CardBody>
                                </Card>

                                <Card bg={cardBg} borderWidth="1px" borderColor="blue.300">
                                  <CardHeader>
                                    <Heading size="sm">Security Features</Heading>
                                  </CardHeader>
                                  <CardBody>
                                    <VStack align="stretch" spacing={2}>
                                      <Tag colorScheme="blue" size="sm">
                                        <TagLabel>JWT Authentication</TagLabel>
                                      </Tag>
                                      <Tag colorScheme="purple" size="sm">
                                        <TagLabel>OAuth2 Support</TagLabel>
                                      </Tag>
                                      <Tag colorScheme="green" size="sm">
                                        <TagLabel>API Key Authentication</TagLabel>
                                      </Tag>
                                    </VStack>
                                  </CardBody>
                                </Card>

                                <Card bg={cardBg} borderWidth="1px" borderColor="orange.300">
                                  <CardHeader>
                                    <Heading size="sm">Performance Features</Heading>
                                  </CardHeader>
                                  <CardBody>
                                    <VStack align="stretch" spacing={2}>
                                      <Tag colorScheme="orange" size="sm">
                                        <TagLabel>Pagination Support</TagLabel>
                                      </Tag>
                                      <Tag colorScheme="red" size="sm">
                                        <TagLabel>Response Filtering</TagLabel>
                                      </Tag>
                                      <Tag colorScheme="yellow" size="sm">
                                        <TagLabel>Cache Headers</TagLabel>
                                      </Tag>
                                    </VStack>
                                  </CardBody>
                                </Card>

                                <Card bg={cardBg} borderWidth="1px" borderColor="purple.300">
                                  <CardHeader>
                                    <Heading size="sm">Monitoring</Heading>
                                  </CardHeader>
                                  <CardBody>
                                    <VStack align="stretch" spacing={2}>
                                      <Tag colorScheme="purple" size="sm">
                                        <TagLabel>Request IDs</TagLabel>
                                      </Tag>
                                      <Tag colorScheme="cyan" size="sm">
                                        <TagLabel>Response Times</TagLabel>
                                      </Tag>
                                      <Tag colorScheme="teal" size="sm">
                                        <TagLabel>Rate Limiting</TagLabel>
                                      </Tag>
                                    </VStack>
                                  </CardBody>
                                </Card>
                              </Grid>
                            </Box>
                          ) : (
                            <Grid templateColumns="1fr 1fr" gap={4}>
                              <Box>
                                <HStack justify="space-between" mb={2}>
                                  <Heading size="sm">Original Specification</Heading>
                                  <Badge colorScheme="gray">v1.0.0</Badge>
                                </HStack>
                                <Box
                                  bg="gray.50"
                                  borderWidth="1px"
                                  borderColor={borderColor}
                                  borderRadius="md"
                                  p={4}
                                  maxH="500px"
                                  overflowY="auto"
                                  fontFamily="mono"
                                  fontSize="xs"
                                >
                                  <pre>{JSON.stringify(mockSpec, null, 2)}</pre>
                                </Box>
                              </Box>
                              
                              <Box>
                                <HStack justify="space-between" mb={2}>
                                  <Heading size="sm">Enhanced Specification</Heading>
                                  <Badge colorScheme="green">v2.0.0</Badge>
                                </HStack>
                                <Box
                                  bg="green.50"
                                  borderWidth="1px"
                                  borderColor="green.300"
                                  borderRadius="md"
                                  p={4}
                                  maxH="500px"
                                  overflowY="auto"
                                  fontFamily="mono"
                                  fontSize="xs"
                                >
                                  <pre>{JSON.stringify(analysisResult.enhanced_openapi, null, 2)}</pre>
                                </Box>
                              </Box>
                            </Grid>
                          )}
                        </VStack>
                      </TabPanel>
                    </TabPanels>
                  </Tabs>
                </CardBody>
              </Card>
            </VStack>
          )}
        </VStack>
      </Container>
    </Box>
  );
};

export default App;
