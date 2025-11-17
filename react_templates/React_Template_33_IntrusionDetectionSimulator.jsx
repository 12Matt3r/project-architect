/**
 * Template #33: Intrusion Detection System Simulator
 * React frontend for security threat detection and analysis
 */

import React, { useState, useCallback, useEffect } from 'react';
import {
  Box,
  Container,
  VStack,
  HStack,
  Heading,
  Text,
  Button,
  Card,
  CardHeader,
  CardBody,
  Grid,
  GridItem,
  Badge,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  Divider,
  useToast,
  FormControl,
  FormLabel,
  Select,
  Progress,
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
  TableContainer,
  Icon,
  Flex,
  Spacer,
  Tag,
  TagLabel,
  Wrap,
  WrapItem,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalFooter,
  ModalBody,
  ModalCloseButton,
  useDisclosure,
  Spinner,
  Tooltip,
  Code,
  List,
  ListItem,
  ListIcon
} from '@chakra-ui/react';
import {
  FiShield,
  FiUpload,
  FiAlertTriangle,
  FiActivity,
  FiEye,
  FiTrendingUp,
  FiGlobe,
  FiClock,
  FiTarget,
  FiZap,
  FiCheckCircle,
  FiXCircle,
  FiInfo,
  FiFileText,
  FiDatabase,
  FiSearch
} from 'react-icons/fi';

// API Configuration
const API_BASE_URL = 'http://localhost:8000';

const IntrusionDetectionSimulator = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResults, setAnalysisResults] = useState(null);
  const [threatIntelligence, setThreatIntelligence] = useState(null);
  const [recentEvents, setRecentEvents] = useState([]);
  const [recentAttempts, setRecentAttempts] = useState([]);
  const [activeTab, setActiveTab] = useState(0);
  const { isOpen: isDetailsModalOpen, onOpen: onDetailsModalOpen, onClose: onDetailsModalClose } = useDisclosure();
  const { isOpen: isFileModalOpen, onOpen: onFileModalOpen, onClose: onFileModalClose } = useDisclosure();
  const [selectedEvent, setSelectedEvent] = useState(null);
  const [selectedAttempt, setSelectedAttempt] = useState(null);
  const toast = useToast();

  // Load threat intelligence and recent events on component mount
  useEffect(() => {
    loadThreatIntelligence();
    loadRecentEvents();
    loadRecentAttempts();
  }, []);

  // Handle file selection
  const handleFileSelect = useCallback((event) => {
    const file = event.target.files[0];
    if (file) {
      // Validate file type
      const allowedTypes = ['.log', '.txt', '.csv', '.json'];
      const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
      
      if (!allowedTypes.includes(fileExtension)) {
        toast({
          title: 'Invalid File Type',
          description: 'Please select a log file (.log, .txt, .csv, or .json)',
          status: 'error',
          duration: 3000,
          isClosable: true,
        });
        return;
      }

      // Validate file size (10MB limit)
      if (file.size > 10 * 1024 * 1024) {
        toast({
          title: 'File Too Large',
          description: 'File size must be less than 10MB',
          status: 'error',
          duration: 3000,
          isClosable: true,
        });
        return;
      }

      setSelectedFile(file);
    }
  }, []);

  // Analyze log file
  const analyzeLogFile = useCallback(async () => {
    if (!selectedFile) {
      toast({
        title: 'No File Selected',
        description: 'Please select a log file to analyze',
        status: 'warning',
        duration: 3000,
        isClosable: true,
      });
      return;
    }

    setIsAnalyzing(true);
    try {
      const formData = new FormData();
      formData.append('log_file', selectedFile);
      formData.append('analysis_type', 'comprehensive');

      const response = await fetch(`${API_BASE_URL}/api/v1/analyze-logs`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Analysis failed');
      }

      const result = await response.json();
      setAnalysisResults(result);

      // Refresh threat intelligence
      loadThreatIntelligence();
      loadRecentEvents();
      loadRecentAttempts();

      toast({
        title: 'Analysis Complete',
        description: `Found ${result.security_events_count} security events with ${result.threat_level} threat level`,
        status: 'success',
        duration: 5000,
        isClosable: true,
      });

    } catch (error) {
      console.error('Error analyzing log file:', error);
      toast({
        title: 'Analysis Failed',
        description: error.message || 'Failed to analyze log file',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setIsAnalyzing(false);
    }
  }, [selectedFile]);

  // Load threat intelligence
  const loadThreatIntelligence = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/threat-intelligence`);
      if (response.ok) {
        const data = await response.json();
        setThreatIntelligence(data);
      }
    } catch (error) {
      console.error('Error loading threat intelligence:', error);
    }
  }, []);

  // Load recent security events
  const loadRecentEvents = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/security-events?limit=10`);
      if (response.ok) {
        const data = await response.json();
        setRecentEvents(data.events || []);
      }
    } catch (error) {
      console.error('Error loading recent events:', error);
    }
  }, []);

  // Load recent intrusion attempts
  const loadRecentAttempts = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/intrusion-attempts?limit=10`);
      if (response.ok) {
        const data = await response.json();
        setRecentAttempts(data.intrusion_attempts || []);
      }
    } catch (error) {
      console.error('Error loading recent attempts:', error);
    }
  }, []);

  // Get severity color
  const getSeverityColor = (severity) => {
    switch (severity?.toLowerCase()) {
      case 'critical':
        return 'red';
      case 'high':
        return 'orange';
      case 'medium':
        return 'yellow';
      case 'low':
        return 'green';
      default:
        return 'gray';
    }
  };

  // Get threat level color
  const getThreatLevelColor = (level) => {
    switch (level?.toUpperCase()) {
      case 'CRITICAL':
        return 'red';
      case 'HIGH':
        return 'orange';
      case 'MEDIUM':
        return 'yellow';
      case 'LOW':
        return 'green';
      default:
        return 'gray';
    }
  };

  // Security event details modal
  const SecurityEventDetails = ({ event, isOpen, onClose }) => (
    <Modal isOpen={isOpen} onClose={onClose} size="xl">
      <ModalOverlay />
      <ModalContent>
        <ModalHeader>
          <HStack spacing={3}>
            <Icon as={FiAlertTriangle} color={`${getSeverityColor(event?.severity)}.500`} />
            <Text>Security Event Details</Text>
            <Badge colorScheme={getSeverityColor(event?.severity)}>
              {event?.severity?.toUpperCase()}
            </Badge>
          </HStack>
        </ModalHeader>
        <ModalCloseButton />
        <ModalBody>
          {event && (
            <VStack align="stretch" spacing={4}>
              <Box>
                <Text fontWeight="bold" mb={2}>Event Information</Text>
                <Grid templateColumns="repeat(2, 1fr)" gap={4}>
                  <Box>
                    <Text fontSize="sm" color="gray.600">Event Type</Text>
                    <Text fontWeight="medium">{event.event_type}</Text>
                  </Box>
                  <Box>
                    <Text fontSize="sm" color="gray.600">Source IP</Text>
                    <Text fontWeight="medium">{event.source_ip}</Text>
                  </Box>
                  <Box>
                    <Text fontSize="sm" color="gray.600">Timestamp</Text>
                    <Text fontWeight="medium">
                      {new Date(event.timestamp).toLocaleString()}
                    </Text>
                  </Box>
                  <Box>
                    <Text fontSize="sm" color="gray.600">Response Code</Text>
                    <Text fontWeight="medium">{event.response_code}</Text>
                  </Box>
                </Grid>
              </Box>

              {event.user_agent && (
                <Box>
                  <Text fontWeight="bold" mb={2}>User Agent</Text>
                  <Code p={2} display="block" fontSize="sm">
                    {event.user_agent}
                  </Code>
                </Box>
              )}

              {event.request_path && (
                <Box>
                  <Text fontWeight="bold" mb={2}>Request Path</Text>
                  <Code p={2} display="block" fontSize="sm">
                    {event.request_path}
                  </Code>
                </Box>
              )}

              {event.detection_rules && (
                <Box>
                  <Text fontWeight="bold" mb={2}>Detection Rules</Text>
                  <Wrap>
                    {JSON.parse(event.detection_rules).map((rule, index) => (
                      <WrapItem key={index}>
                        <Tag colorScheme="blue" size="sm">
                          <TagLabel>{rule}</TagLabel>
                        </Tag>
                      </WrapItem>
                    ))}
                  </Wrap>
                </Box>
              )}

              {event.additional_data && (
                <Box>
                  <Text fontWeight="bold" mb={2}>Additional Data</Text>
                  <Code p={2} display="block" fontSize="sm" maxH="200px" overflowY="auto">
                    {JSON.stringify(JSON.parse(event.additional_data), null, 2)}
                  </Code>
                </Box>
              )}
            </VStack>
          )}
        </ModalBody>
        <ModalFooter>
          <Button onClick={onClose}>Close</Button>
        </ModalFooter>
      </ModalContent>
    </Modal>
  );

  // Intrusion attempt details modal
  const IntrusionAttemptDetails = ({ attempt, isOpen, onClose }) => (
    <Modal isOpen={isOpen} onClose={onClose} size="xl">
      <ModalOverlay />
      <ModalContent>
        <ModalHeader>
          <HStack spacing={3}>
            <Icon as={FiTarget} color="purple.500" />
            <Text>Intrusion Attempt Details</Text>
            <Badge colorScheme="purple">
              {Math.round((attempt?.confidence_score || 0) * 100)}% Confidence
            </Badge>
          </HStack>
        </ModalHeader>
        <ModalCloseButton />
        <ModalBody>
          {attempt && (
            <VStack align="stretch" spacing={4}>
              <Box>
                <Text fontWeight="bold" mb={2}>Attack Information</Text>
                <Grid templateColumns="repeat(2, 1fr)" gap={4}>
                  <Box>
                    <Text fontSize="sm" color="gray.600">Attack Type</Text>
                    <Text fontWeight="medium">{attempt.attack_type}</Text>
                  </Box>
                  <Box>
                    <Text fontSize="sm" color="gray.600">Confidence Score</Text>
                    <Text fontWeight="medium">
                      {Math.round((attempt.confidence_score || 0) * 100)}%
                    </Text>
                  </Box>
                </Grid>
              </Box>

              <Box>
                <Text fontWeight="bold" mb={2}>Attack Vector</Text>
                <Text>{attempt.attack_vector}</Text>
              </Box>

              {attempt.mitigation_suggestions && (
                <Box>
                  <Text fontWeight="bold" mb={2}>Mitigation Suggestions</Text>
                  <List spacing={2}>
                    {JSON.parse(attempt.mitigation_suggestions).map((suggestion, index) => (
                      <ListItem key={index}>
                        <ListIcon as={FiCheckCircle} color="green.500" />
                        {suggestion}
                      </ListItem>
                    ))}
                  </List>
                </Box>
              )}

              <Box>
                <Text fontWeight="bold" mb={2}>False Positive Likelihood</Text>
                <Badge 
                  colorScheme={attempt.false_positive_likelihood < 0.05 ? 'green' : 
                              attempt.false_positive_likelihood < 0.1 ? 'yellow' : 'red'}
                >
                  {Math.round((attempt.false_positive_likelihood || 0) * 100)}%
                </Badge>
              </Box>
            </VStack>
          )}
        </ModalBody>
        <ModalFooter>
          <Button onClick={onClose}>Close</Button>
        </ModalFooter>
      </ModalContent>
    </Modal>
  );

  return (
    <Container maxW="7xl" py={8}>
      <VStack spacing={8} align="stretch">
        {/* Header */}
        <Box textAlign="center">
          <Heading size="2xl" mb={4}>
            Intrusion Detection System Simulator
          </Heading>
          <Text fontSize="lg" color="gray.600" maxW="3xl" mx="auto">
            Advanced security monitoring system that analyzes server logs to detect spam and intrusion attempts.
            Identifies patterns including suspicious user agents and brute force attacks.
          </Text>
        </Box>

        {/* File Upload Section */}
        <Card>
          <CardHeader>
            <HStack spacing={3}>
              <Icon as={FiUpload} color="blue.500" boxSize={6} />
              <Box>
                <Heading size="lg">Log File Analysis</Heading>
                <Text color="gray.600">Upload server logs for security threat analysis</Text>
              </Box>
            </HStack>
          </CardHeader>
          <CardBody>
            <Grid templateColumns={{ base: '1fr', lg: '2fr 1fr' }} gap={6}>
              <GridItem>
                <VStack align="stretch" spacing={4}>
                  {/* File Upload */}
                  <FormControl>
                    <FormLabel>Log File</FormLabel>
                    <Box
                      border="2px dashed"
                      borderColor={selectedFile ? "green.300" : "gray.300"}
                      borderRadius="md"
                      p={6}
                      textAlign="center"
                      cursor="pointer"
                      onClick={() => document.getElementById('log-upload').click()}
                      _hover={{ borderColor: "blue.400" }}
                    >
                      {selectedFile ? (
                        <VStack spacing={3}>
                          <Icon as={FiFileText} boxSize={8} color="green.500" />
                          <Text fontWeight="bold">{selectedFile.name}</Text>
                          <Text fontSize="sm" color="gray.600">
                            {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                          </Text>
                          <Button 
                            size="sm" 
                            variant="outline"
                            onClick={(e) => {
                              e.stopPropagation();
                              setSelectedFile(null);
                            }}
                          >
                            Remove File
                          </Button>
                        </VStack>
                      ) : (
                        <VStack spacing={3}>
                          <Icon as={FiUpload} boxSize={8} color="gray.400" />
                          <Text color="gray.600">
                            Click to upload a log file for analysis
                          </Text>
                          <Text fontSize="sm" color="gray.500">
                            Supports: .log, .txt, .csv, .json (Max 10MB)
                          </Text>
                        </VStack>
                      )}
                      <input
                        id="log-upload"
                        type="file"
                        accept=".log,.txt,.csv,.json"
                        onChange={handleFileSelect}
                        style={{ display: 'none' }}
                      />
                    </Box>
                  </FormControl>

                  {/* Analysis Progress */}
                  {isAnalyzing && (
                    <Box p={4} bg="blue.50" borderRadius="md">
                      <VStack spacing={3}>
                        <HStack spacing={3} w="full">
                          <Spinner size="sm" color="blue.500" />
                          <Text>Analyzing log file...</Text>
                        </HStack>
                        <Progress size="sm" isIndeterminate colorScheme="blue" w="full" />
                        <Text fontSize="sm" color="gray.600">
                          Running pattern recognition and threat detection
                        </Text>
                      </VStack>
                    </Box>
                  )}
                </VStack>
              </GridItem>

              <GridItem>
                <VStack align="stretch" spacing={4}>
                  {/* Detection Capabilities */}
                  <Box p={4} bg="purple.50" borderRadius="md">
                    <Heading size="md" mb={3}>Detection Capabilities</Heading>
                    <VStack align="stretch" spacing={2}>
                      <HStack>
                        <Icon as={FiCheckCircle} color="green.500" />
                        <Text fontSize="sm">Brute Force Attacks (4+ failed logins)</Text>
                      </HStack>
                      <HStack>
                        <Icon as={FiCheckCircle} color="green.500" />
                        <Text fontSize="sm">Suspicious User Agent Detection</Text>
                      </HStack>
                      <HStack>
                        <Icon as={FiCheckCircle} color="green.500" />
                        <Text fontSize="sm">SQL Injection Attempts</Text>
                      </HStack>
                      <HStack>
                        <Icon as={FiCheckCircle} color="green.500" />
                        <Text fontSize="sm">XSS Attack Patterns</Text>
                      </HStack>
                      <HStack>
                        <Icon as={FiCheckCircle} color="green.500" />
                        <Text fontSize="sm">Path Traversal Attempts</Text>
                      </HStack>
                    </VStack>
                  </Box>

                  {/* Supported Formats */}
                  <Box p={4} bg="gray.50" borderRadius="md">
                    <Heading size="md" mb={3}>Supported Formats</Heading>
                    <VStack align="stretch" spacing={1}>
                      <Text fontSize="sm">• Apache Combined Log Format</Text>
                      <Text fontSize="sm">• Nginx Log Format</Text>
                      <Text fontSize="sm">• JSON Lines Format</Text>
                      <Text fontSize="sm">• CSV Format</Text>
                      <Text fontSize="sm">• IIS W3C Format</Text>
                    </VStack>
                  </Box>

                  {/* Analyze Button */}
                  <Button
                    size="lg"
                    colorScheme="blue"
                    leftIcon={isAnalyzing ? <Spinner size="sm" /> : <FiSearch />}
                    onClick={analyzeLogFile}
                    isLoading={isAnalyzing}
                    loadingText="Analyzing..."
                    isDisabled={!selectedFile || isAnalyzing}
                  >
                    Analyze Log File
                  </Button>
                </VStack>
              </GridItem>
            </Grid>
          </CardBody>
        </Card>

        {/* Analysis Results */}
        {analysisResults && (
          <>
            {/* Analysis Summary */}
            <Card>
              <CardHeader>
                <HStack spacing={3}>
                  <Icon as={FiTrendingUp} color="green.500" boxSize={6} />
                  <Heading size="lg">Analysis Results</Heading>
                  <Badge colorScheme={getThreatLevelColor(analysisResults.threat_level)} size="lg">
                    {analysisResults.threat_level} THREAT LEVEL
                  </Badge>
                </HStack>
              </CardHeader>
              <CardBody>
                <Grid templateColumns={{ base: '1fr', md: 'repeat(4, 1fr)' }} gap={6}>
                  <Stat>
                    <StatLabel>Total Log Entries</StatLabel>
                    <StatNumber color="blue.500">
                      {analysisResults.total_entries?.toLocaleString()}
                    </StatNumber>
                  </Stat>
                  <Stat>
                    <StatLabel>Security Events</StatLabel>
                    <StatNumber color="orange.500">
                      {analysisResults.security_events_count}
                    </StatNumber>
                  </Stat>
                  <Stat>
                    <StatLabel>Intrusion Attempts</StatLabel>
                    <StatNumber color="red.500">
                      {analysisResults.intrusion_attempts_count}
                    </StatNumber>
                  </Stat>
                  <Stat>
                    <StatLabel>Parse Errors</StatLabel>
                    <StatNumber color="gray.500">
                      {analysisResults.parse_errors ? analysisResults.parse_errors.split(';').length : 0}
                    </StatNumber>
                  </Stat>
                </Grid>

                <Divider my={6} />

                {/* Recommendations */}
                {analysisResults.recommendations && analysisResults.recommendations.length > 0 && (
                  <Box>
                    <Heading size="md" mb={4}>Security Recommendations</Heading>
                    <VStack align="stretch" spacing={2}>
                      {analysisResults.recommendations.map((rec, index) => (
                        <Alert key={index} status="info" variant="left-accent">
                          <AlertIcon />
                          <AlertDescription fontSize="sm">
                            {rec}
                          </AlertDescription>
                        </Alert>
                      ))}
                    </VStack>
                  </Box>
                )}
              </CardBody>
            </Card>

            {/* Detailed Results Tabs */}
            <Card>
              <CardBody>
                <Tabs index={activeTab} onChange={setActiveTab}>
                  <TabList>
                    <Tab>Security Events</Tab>
                    <Tab>Intrusion Attempts</Tab>
                    <Tab>Analysis Summary</Tab>
                  </TabList>

                  <TabPanels>
                    {/* Security Events Tab */}
                    <TabPanel>
                      {analysisResults.security_events && analysisResults.security_events.length > 0 ? (
                        <TableContainer>
                          <Table variant="simple">
                            <Thead>
                              <Tr>
                                <Th>Type</Th>
                                <Th>Severity</Th>
                                <Th>Source IP</Th>
                                <Th>Timestamp</Th>
                                <Th>Confidence</Th>
                                <Th>Actions</Th>
                              </Tr>
                            </Thead>
                            <Tbody>
                              {analysisResults.security_events.map((event) => (
                                <Tr key={event.id}>
                                  <Td>
                                    <Text fontSize="sm" fontWeight="medium">
                                      {event.event_type}
                                    </Text>
                                  </Td>
                                  <Td>
                                    <Badge colorScheme={getSeverityColor(event.severity)} size="sm">
                                      {event.severity}
                                    </Badge>
                                  </Td>
                                  <Td>
                                    <Text fontSize="sm">{event.source_ip}</Text>
                                  </Td>
                                  <Td>
                                    <Text fontSize="sm">
                                      {new Date(event.timestamp).toLocaleString()}
                                    </Text>
                                  </Td>
                                  <Td>
                                    <Badge 
                                      colorScheme={event.confidence_score > 0.8 ? 'green' : 'yellow'} 
                                      size="sm"
                                    >
                                      {Math.round((event.confidence_score || 0) * 100)}%
                                    </Badge>
                                  </Td>
                                  <Td>
                                    <Button
                                      size="sm"
                                      variant="outline"
                                      leftIcon={<FiEye />}
                                      onClick={() => {
                                        setSelectedEvent(event);
                                        onDetailsModalOpen();
                                      }}
                                    >
                                      Details
                                    </Button>
                                  </Td>
                                </Tr>
                              ))}
                            </Tbody>
                          </Table>
                        </TableContainer>
                      ) : (
                        <Alert status="success">
                          <AlertIcon />
                          <AlertTitle>No Security Events</AlertTitle>
                          <AlertDescription>
                            No security threats detected in the analyzed log file.
                          </AlertDescription>
                        </Alert>
                      )}
                    </TabPanel>

                    {/* Intrusion Attempts Tab */}
                    <TabPanel>
                      {analysisResults.intrusion_attempts && analysisResults.intrusion_attempts.length > 0 ? (
                        <TableContainer>
                          <Table variant="simple">
                            <Thead>
                              <Tr>
                                <Th>Attack Type</Th>
                                <Th>Confidence</Th>
                                <Th>Attack Vector</Th>
                                <Th>False Positive</Th>
                                <Th>Actions</Th>
                              </Tr>
                            </Thead>
                            <Tbody>
                              {analysisResults.intrusion_attempts.map((attempt) => (
                                <Tr key={attempt.id}>
                                  <Td>
                                    <Text fontSize="sm" fontWeight="medium">
                                      {attempt.attack_type}
                                    </Text>
                                  </Td>
                                  <Td>
                                    <Badge 
                                      colorScheme={attempt.confidence_score > 0.8 ? 'green' : 'yellow'} 
                                      size="sm"
                                    >
                                      {Math.round((attempt.confidence_score || 0) * 100)}%
                                    </Badge>
                                  </Td>
                                  <Td>
                                    <Text fontSize="sm" maxW="300px" isTruncated>
                                      {attempt.attack_vector}
                                    </Text>
                                  </Td>
                                  <Td>
                                    <Badge 
                                      colorScheme={attempt.false_positive_likelihood < 0.05 ? 'green' : 'yellow'} 
                                      size="sm"
                                    >
                                      {Math.round((attempt.false_positive_likelihood || 0) * 100)}%
                                    </Badge>
                                  </Td>
                                  <Td>
                                    <Button
                                      size="sm"
                                      variant="outline"
                                      leftIcon={<FiEye />}
                                      onClick={() => {
                                        setSelectedAttempt(attempt);
                                        onFileModalOpen();
                                      }}
                                    >
                                      Details
                                    </Button>
                                  </Td>
                                </Tr>
                              ))}
                            </Tbody>
                          </Table>
                        </TableContainer>
                      ) : (
                        <Alert status="success">
                          <AlertIcon />
                          <AlertTitle>No Intrusion Attempts</AlertTitle>
                          <AlertDescription>
                            No intrusion attempts detected in the analyzed log file.
                          </AlertDescription>
                        </Alert>
                      )}
                    </TabPanel>

                    {/* Analysis Summary Tab */}
                    <TabPanel>
                      {analysisResults.analysis_summary && (
                        <VStack align="stretch" spacing={6}>
                          {/* Threat Level Overview */}
                          <Box p={4} bg={`${getThreatLevelColor(analysisResults.threat_level)}.50`} borderRadius="md">
                            <HStack spacing={3} mb={3}>
                              <Icon as={FiShield} color={`${getThreatLevelColor(analysisResults.threat_level)}.500`} />
                              <Heading size="md">Threat Level: {analysisResults.threat_level}</Heading>
                            </HStack>
                            <Text>{analysisResults.analysis_summary.summary}</Text>
                          </Box>

                          {/* Severity Breakdown */}
                          <Grid templateColumns={{ base: '1fr', md: 'repeat(4, 1fr)' }} gap={4}>
                            {Object.entries(analysisResults.analysis_summary.severity_breakdown || {}).map(([severity, count]) => (
                              <Box key={severity} p={3} bg="gray.50" borderRadius="md" textAlign="center">
                                <Text fontSize="2xl" fontWeight="bold" color={`${getSeverityColor(severity)}.500`}>
                                  {count}
                                </Text>
                                <Text fontSize="sm" color="gray.600" textTransform="capitalize">
                                  {severity} Severity
                                </Text>
                              </Box>
                            ))}
                          </Grid>

                          {/* Top Source IPs */}
                          {analysisResults.analysis_summary.top_source_ips && analysisResults.analysis_summary.top_source_ips.length > 0 && (
                            <Box>
                              <Heading size="md" mb={3}>Top Source IPs</Heading>
                              <Wrap>
                                {analysisResults.analysis_summary.top_source_ips.map(([ip, count]) => (
                                  <WrapItem key={ip}>
                                    <Tag colorScheme="red" size="lg">
                                      <TagLabel>{ip} ({count} events)</TagLabel>
                                    </Tag>
                                  </WrapItem>
                                ))}
                              </Wrap>
                            </Box>
                          )}
                        </VStack>
                      )}
                    </TabPanel>
                  </TabPanels>
                </Tabs>
              </CardBody>
            </Card>
          </>
        )}

        {/* Threat Intelligence Dashboard */}
        {threatIntelligence && (
          <Card>
            <CardHeader>
              <Heading size="lg">Threat Intelligence Dashboard</Heading>
              <Text color="gray.600">Real-time security monitoring and analysis</Text>
            </CardHeader>
            <CardBody>
              <Grid templateColumns={{ base: '1fr', md: 'repeat(3, 1fr)' }} gap={6}>
                <Stat>
                  <StatLabel>Total Security Events</StatLabel>
                  <StatNumber color="red.500">
                    {threatIntelligence.overview?.total_security_events || 0}
                  </StatNumber>
                </Stat>
                <Stat>
                  <StatLabel>Intrusion Attempts</StatLabel>
                  <StatNumber color="orange.500">
                    {threatIntelligence.overview?.total_intrusion_attempts || 0}
                  </StatNumber>
                </Stat>
                <Stat>
                  <StatLabel>Analysis Sessions</StatLabel>
                  <StatNumber color="blue.500">
                    {threatIntelligence.overview?.total_analysis_sessions || 0}
                  </StatNumber>
                </Stat>
              </Grid>

              <Divider my={6} />

              {/* Recent High-Confidence Events */}
              {threatIntelligence.high_confidence_events && threatIntelligence.high_confidence_events.length > 0 && (
                <Box>
                  <Heading size="md" mb={3}>Recent High-Confidence Events</Heading>
                  <TableContainer>
                    <Table variant="simple" size="sm">
                      <Thead>
                        <Tr>
                          <Th>Event Type</Th>
                          <Th>Severity</Th>
                          <Th>Source IP</Th>
                          <Th>Confidence</Th>
                          <Th>Timestamp</Th>
                        </Tr>
                      </Thead>
                      <Tbody>
                        {threatIntelligence.high_confidence_events.slice(0, 5).map((event) => (
                          <Tr key={event.id}>
                            <Td>{event.event_type}</Td>
                            <Td>
                              <Badge colorScheme={getSeverityColor(event.severity)} size="sm">
                                {event.severity}
                              </Badge>
                            </Td>
                            <Td>{event.source_ip}</Td>
                            <Td>
                              <Badge colorScheme="green" size="sm">
                                {Math.round((event.confidence_score || 0) * 100)}%
                              </Badge>
                            </Td>
                            <Td>
                              <Text fontSize="sm">
                                {new Date(event.timestamp).toLocaleString()}
                              </Text>
                            </Td>
                          </Tr>
                        ))}
                      </Tbody>
                    </Table>
                  </TableContainer>
                </Box>
              )}
            </CardBody>
          </Card>
        )}

        {/* Modals */}
        <SecurityEventDetails 
          event={selectedEvent} 
          isOpen={isDetailsModalOpen} 
          onClose={() => {
            onDetailsModalClose();
            setSelectedEvent(null);
          }} 
        />

        <IntrusionAttemptDetails 
          attempt={selectedAttempt} 
          isOpen={isFileModalOpen} 
          onClose={() => {
            onFileModalClose();
            setSelectedAttempt(null);
          }} 
        />
      </VStack>
    </Container>
  );
};

export default IntrusionDetectionSimulator;