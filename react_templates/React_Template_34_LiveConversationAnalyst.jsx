/**
 * Template #34: Live Conversation Analyst
 * React frontend for conversation analysis and decision tree visualization
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
  ListIcon,
  Avatar,
  AvatarBadge,
  AvatarGroup
} from '@chakra-ui/react';
import {
  FiMessageSquare,
  FiUpload,
  FiUsers,
  FiTrendingUp,
  FiTarget,
  FiHeart,
  FiSmile,
  FiFrown,
  FiMeh,
  FiZap,
  FiBrain,
  FiEye,
  FiDownload,
  FiRefreshCw,
  FiActivity,
  FiClock,
  FiUser,
  FiCheckCircle,
  FiAlertCircle,
  FiInfo
} from 'react-icons/fi';

// API Configuration
const API_BASE_URL = 'http://localhost:8000';

const LiveConversationAnalyst = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResults, setAnalysisResults] = useState(null);
  const [conversationInsights, setConversationInsights] = useState(null);
  const [recentSessions, setRecentSessions] = useState([]);
  const [activeTab, setActiveTab] = useState(0);
  const { isOpen: isSpeakerModalOpen, onOpen: onSpeakerModalOpen, onClose: onSpeakerModalClose } = useDisclosure();
  const { isOpen: isDecisionModalOpen, onOpen: onDecisionModalOpen, onClose: onDecisionModalClose } = useDisclosure();
  const [selectedSpeaker, setSelectedSpeaker] = useState(null);
  const [selectedDecision, setSelectedDecision] = useState(null);
  const toast = useToast();

  // Load conversation insights and recent sessions on component mount
  useEffect(() => {
    loadConversationInsights();
    loadRecentSessions();
  }, []);

  // Handle file selection
  const handleFileSelect = useCallback((event) => {
    const file = event.target.files[0];
    if (file) {
      // Validate file type
      const allowedTypes = ['.txt', '.csv', '.json'];
      const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
      
      if (!allowedTypes.includes(fileExtension)) {
        toast({
          title: 'Invalid File Type',
          description: 'Please select a transcript file (.txt, .csv, or .json)',
          status: 'error',
          duration: 3000,
          isClosable: true,
        });
        return;
      }

      // Validate file size (5MB limit)
      if (file.size > 5 * 1024 * 1024) {
        toast({
          title: 'File Too Large',
          description: 'File size must be less than 5MB',
          status: 'error',
          duration: 3000,
          isClosable: true,
        });
        return;
      }

      setSelectedFile(file);
    }
  }, []);

  // Analyze transcript
  const analyzeTranscript = useCallback(async () => {
    if (!selectedFile) {
      toast({
        title: 'No File Selected',
        description: 'Please select a transcript file to analyze',
        status: 'warning',
        duration: 3000,
        isClosable: true,
      });
      return;
    }

    setIsAnalyzing(true);
    try {
      const formData = new FormData();
      formData.append('transcript_file', selectedFile);
      formData.append('analysis_type', 'comprehensive');

      const response = await fetch(`${API_BASE_URL}/api/v1/analyze-conversation`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Analysis failed');
      }

      const result = await response.json();
      setAnalysisResults(result);

      // Refresh insights and sessions
      loadConversationInsights();
      loadRecentSessions();

      toast({
        title: 'Analysis Complete',
        description: `Analyzed ${result.total_segments} segments with ${result.speakers.length} speakers`,
        status: 'success',
        duration: 5000,
        isClosable: true,
      });

    } catch (error) {
      console.error('Error analyzing transcript:', error);
      toast({
        title: 'Analysis Failed',
        description: error.message || 'Failed to analyze transcript',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setIsAnalyzing(false);
    }
  }, [selectedFile]);

  // Load conversation insights
  const loadConversationInsights = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/conversation-insights`);
      if (response.ok) {
        const data = await response.json();
        setConversationInsights(data);
      }
    } catch (error) {
      console.error('Error loading conversation insights:', error);
    }
  }, []);

  // Load recent sessions
  const loadRecentSessions = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/speaker-analysis?limit=10`);
      if (response.ok) {
        const data = await response.json();
        setRecentSessions(data.speaker_analysis || []);
      }
    } catch (error) {
      console.error('Error loading recent sessions:', error);
    }
  }, []);

  // Get emotional state color and icon
  const getEmotionalStateInfo = (emotion) => {
    switch (emotion?.toLowerCase()) {
      case 'very_positive':
      case 'positive':
        return { color: 'green', icon: FiSmile };
      case 'very_negative':
      case 'negative':
        return { color: 'red', icon: FiFrown };
      case 'excited':
        return { color: 'orange', icon: FiZap };
      case 'frustrated':
        return { color: 'red', icon: FiFrown };
      case 'confused':
        return { color: 'yellow', icon: FiMeh };
      case 'engaged':
        return { color: 'blue', icon: FiActivity };
      case 'disengaged':
        return { color: 'gray', icon: FiMeh };
      default:
        return { color: 'gray', icon: FiMeh };
    }
  };

  // Get consensus level color
  const getConsensusColor = (consensus) => {
    switch (consensus?.toLowerCase()) {
      case 'unanimous':
      case 'strong_consensus':
        return 'green';
      case 'moderate_consensus':
        return 'yellow';
      case 'minority_support':
        return 'orange';
      case 'no_consensus':
        return 'red';
      default:
        return 'gray';
    }
  };

  // Speaker profile modal
  const SpeakerProfileModal = ({ speaker, isOpen, onClose }) => {
    if (!speaker) return null;

    const emotionalInfo = getEmotionalStateInfo(speaker.dominant_emotion);
    const EmotionalIcon = emotionalInfo.icon;

    return (
      <Modal isOpen={isOpen} onClose={onClose} size="xl">
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>
            <HStack spacing={3}>
              <Avatar size="md" name={speaker.name}>
                <AvatarBadge boxSize="1.0em" bg={`${emotionalInfo.color}.500`}>
                  <Icon as={EmotionalIcon} color="white" boxSize={3} />
                </AvatarBadge>
              </Avatar>
              <Box>
                <Text fontSize="lg" fontWeight="bold">{speaker.name}</Text>
                <Text fontSize="sm" color="gray.600">{speaker.role || 'Participant'}</Text>
              </Box>
            </HStack>
          </ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <VStack align="stretch" spacing={6}>
              {/* Engagement Metrics */}
              <Box>
                <Heading size="md" mb={3}>Engagement Metrics</Heading>
                <Grid templateColumns="repeat(3, 1fr)" gap={4}>
                  <Stat>
                    <StatLabel>Engagement Score</StatLabel>
                    <StatNumber color={`${emotionalInfo.color}.500`}>
                      {Math.round((speaker.engagement_score || 0) * 100)}%
                    </StatNumber>
                  </Stat>
                  <Stat>
                    <StatLabel>Speaking Time</StatLabel>
                    <StatNumber color="blue.500">
                      {Math.round(speaker.speaking_time_percentage || 0)}%
                    </StatNumber>
                  </Stat>
                  <Stat>
                    <StatLabel>Total Statements</StatLabel>
                    <StatNumber color="purple.500">
                      {speaker.total_statements || 0}
                    </StatNumber>
                  </Stat>
                </Grid>
              </Box>

              {/* Emotional Analysis */}
              <Box>
                <Heading size="md" mb={3}>Emotional Profile</Heading>
                <VStack align="stretch" spacing={3}>
                  <HStack justify="space-between">
                    <Text>Dominant Emotion:</Text>
                    <HStack spacing={2}>
                      <Icon as={EmotionalIcon} color={`${emotionalInfo.color}.500`} />
                      <Badge colorScheme={emotionalInfo.color}>
                        {speaker.dominant_emotion?.replace('_', ' ').toUpperCase()}
                      </Badge>
                    </HStack>
                  </HStack>
                  <HStack justify="space-between">
                    <Text>Average Sentiment:</Text>
                    <Badge colorScheme={speaker.average_sentiment > 0 ? 'green' : 'red'}>
                      {speaker.average_sentiment?.toFixed(2) || '0.00'}
                    </Badge>
                  </HStack>
                  <HStack justify="space-between">
                    <Text>Emotional Intensity:</Text>
                    <Badge colorScheme={speaker.average_intensity > 0.7 ? 'orange' : 'gray'}>
                      {Math.round((speaker.average_intensity || 0) * 100)}%
                    </Badge>
                  </HStack>
                </VStack>
              </Box>

              {/* Emotional Peaks and Lows */}
              <Grid templateColumns="repeat(2, 1fr)" gap={4}>
                <Box>
                  <Heading size="sm" mb={2}>Emotional Peaks</Heading>
                  {speaker.emotional_peaks && speaker.emotional_peaks.length > 0 ? (
                    <VStack align="stretch" spacing={1}>
                      {speaker.emotional_peaks.slice(0, 5).map((peak, index) => (
                        <Text key={index} fontSize="sm">
                          <Badge colorScheme="green" size="sm" mr={2}>
                            {peak.emotion}
                          </Badge>
                          Segment {peak.timestamp}
                        </Text>
                      ))}
                    </VStack>
                  ) : (
                    <Text fontSize="sm" color="gray.500">No significant peaks detected</Text>
                  )}
                </Box>
                <Box>
                  <Heading size="sm" mb={2}>Emotional Lows</Heading>
                  {speaker.emotional_lows && speaker.emotional_lows.length > 0 ? (
                    <VStack align="stretch" spacing={1}>
                      {speaker.emotional_lows.slice(0, 5).map((low, index) => (
                        <Text key={index} fontSize="sm">
                          <Badge colorScheme="red" size="sm" mr={2}>
                            {low.emotion}
                          </Badge>
                          Segment {low.timestamp}
                        </Text>
                      ))}
                    </VStack>
                  ) : (
                    <Text fontSize="sm" color="gray.500">No significant lows detected</Text>
                  )}
                </Box>
              </Grid>
            </VStack>
          </ModalBody>
          <ModalFooter>
            <Button onClick={onClose}>Close</Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    );
  };

  // Decision point modal
  const DecisionPointModal = ({ decision, isOpen, onClose }) => {
    if (!decision) return null;

    return (
      <Modal isOpen={isOpen} onClose={onClose} size="xl">
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>
            <HStack spacing={3}>
              <Icon as={FiTarget} color="blue.500" />
              <Text>Decision Point Details</Text>
              <Badge colorScheme={getConsensusColor(decision.consensus_level)}>
                {decision.consensus_level?.replace('_', ' ').toUpperCase()}
              </Badge>
            </HStack>
          </ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <VStack align="stretch" spacing={4}>
              <Box>
                <Text fontWeight="bold" mb={2}>Decision</Text>
                <Text>{decision.decision_text}</Text>
              </Box>

              <Grid templateColumns="repeat(2, 1fr)" gap={4}>
                <Box>
                  <Text fontSize="sm" color="gray.600">Importance Score</Text>
                  <Text fontSize="lg" fontWeight="bold" color="blue.500">
                    {Math.round((decision.importance_score || 0) * 100)}%
                  </Text>
                </Box>
                <Box>
                  <Text fontSize="sm" color="gray.600">Timestamp</Text>
                  <Text fontSize="lg" fontWeight="bold">
                    Segment {decision.timestamp}
                  </Text>
                </Box>
              </Grid>

              <Box>
                <Text fontWeight="bold" mb={2}>Participants</Text>
                <Wrap>
                  {decision.participants?.map((participant, index) => (
                    <WrapItem key={index}>
                      <Tag colorScheme="blue" size="sm">
                        <TagLabel>{participant}</TagLabel>
                      </Tag>
                    </WrapItem>
                  ))}
                </Wrap>
              </Box>

              {decision.context_summary && (
                <Box>
                  <Text fontWeight="bold" mb={2}>Context</Text>
                  <Text fontSize="sm" color="gray.600">{decision.context_summary}</Text>
                </Box>
              )}

              {decision.supporting_evidence && decision.supporting_evidence.length > 0 && (
                <Box>
                  <Text fontWeight="bold" mb={2}>Supporting Evidence</Text>
                  <List spacing={2}>
                    {decision.supporting_evidence.map((evidence, index) => (
                      <ListItem key={index} fontSize="sm">
                        <ListIcon as={FiCheckCircle} color="green.500" />
                        {evidence}
                      </ListItem>
                    ))}
                  </List>
                </Box>
              )}
            </VStack>
          </ModalBody>
          <ModalFooter>
            <Button onClick={onClose}>Close</Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    );
  };

  return (
    <Container maxW="7xl" py={8}>
      <VStack spacing={8} align="stretch">
        {/* Header */}
        <Box textAlign="center">
          <Heading size="2xl" mb={4}>
            Live Conversation Analyst
          </Heading>
          <Text fontSize="lg" color="gray.600" maxW="3xl" mx="auto">
            Advanced conversation analysis system that analyzes meeting transcripts to identify 
            emotional states, decision points, and conversational flow patterns.
          </Text>
        </Box>

        {/* File Upload Section */}
        <Card>
          <CardHeader>
            <HStack spacing={3}>
              <Icon as={FiUpload} color="blue.500" boxSize={6} />
              <Box>
                <Heading size="lg">Transcript Analysis</Heading>
                <Text color="gray.600">Upload meeting transcript for comprehensive analysis</Text>
              </Box>
            </HStack>
          </CardHeader>
          <CardBody>
            <Grid templateColumns={{ base: '1fr', lg: '2fr 1fr' }} gap={6}>
              <GridItem>
                <VStack align="stretch" spacing={4}>
                  {/* File Upload */}
                  <FormControl>
                    <FormLabel>Meeting Transcript</FormLabel>
                    <Box
                      border="2px dashed"
                      borderColor={selectedFile ? "green.300" : "gray.300"}
                      borderRadius="md"
                      p={6}
                      textAlign="center"
                      cursor="pointer"
                      onClick={() => document.getElementById('transcript-upload').click()}
                      _hover={{ borderColor: "blue.400" }}
                    >
                      {selectedFile ? (
                        <VStack spacing={3}>
                          <Icon as={FiMessageSquare} boxSize={8} color="green.500" />
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
                            Click to upload a transcript file for analysis
                          </Text>
                          <Text fontSize="sm" color="gray.500">
                            Supports: .txt, .csv, .json (Max 5MB)
                          </Text>
                        </VStack>
                      )}
                      <input
                        id="transcript-upload"
                        type="file"
                        accept=".txt,.csv,.json"
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
                          <Text>Analyzing conversation...</Text>
                        </HStack>
                        <Progress size="sm" isIndeterminate colorScheme="blue" w="full" />
                        <Text fontSize="sm" color="gray.600">
                          Processing emotional states and decision points
                        </Text>
                      </VStack>
                    </Box>
                  )}
                </VStack>
              </GridItem>

              <GridItem>
                <VStack align="stretch" spacing={4}>
                  {/* Analysis Capabilities */}
                  <Box p={4} bg="purple.50" borderRadius="md">
                    <Heading size="md" mb={3}>Analysis Capabilities</Heading>
                    <VStack align="stretch" spacing={2}>
                      <HStack>
                        <Icon as={FiHeart} color="red.500" />
                        <Text fontSize="sm">Emotional State Detection</Text>
                      </HStack>
                      <HStack>
                        <Icon as={FiTrendingUp} color="green.500" />
                        <Text fontSize="sm">Peak/Low Identification</Text>
                      </HStack>
                      <HStack>
                        <Icon as={FiTarget} color="blue.500" />
                        <Text fontSize="sm">Decision Point Detection</Text>
                      </HStack>
                      <HStack>
                        <Icon as={FiBrain} color="purple.500" />
                        <Text fontSize="sm">Speaker Profiling</Text>
                      </HStack>
                      <HStack>
                        <Icon as={FiActivity} color="orange.500" />
                        <Text fontSize="sm">Engagement Analysis</Text>
                      </HStack>
                    </VStack>
                  </Box>

                  {/* Supported Formats */}
                  <Box p={4} bg="gray.50" borderRadius="md">
                    <Heading size="md" mb={3}>Supported Formats</Heading>
                    <VStack align="stretch" spacing={1}>
                      <Text fontSize="sm">• Speaker: Content format</Text>
                      <Text fontSize="sm">• [Time] Speaker: Content format</Text>
                      <Text fontSize="sm">• Name - Content format</Text>
                      <Text fontSize="sm">• Numbered segment format</Text>
                    </VStack>
                  </Box>

                  {/* Analyze Button */}
                  <Button
                    size="lg"
                    colorScheme="blue"
                    leftIcon={isAnalyzing ? <Spinner size="sm" /> : <FiBrain />}
                    onClick={analyzeTranscript}
                    isLoading={isAnalyzing}
                    loadingText="Analyzing..."
                    isDisabled={!selectedFile || isAnalyzing}
                  >
                    Analyze Transcript
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
                </HStack>
              </CardHeader>
              <CardBody>
                <Grid templateColumns={{ base: '1fr', md: 'repeat(4, 1fr)' }} gap={6}>
                  <Stat>
                    <StatLabel>Total Segments</StatLabel>
                    <StatNumber color="blue.500">
                      {analysisResults.total_segments?.toLocaleString()}
                    </StatNumber>
                  </Stat>
                  <Stat>
                    <StatLabel>Speakers</StatLabel>
                    <StatNumber color="purple.500">
                      {analysisResults.speakers?.length || 0}
                    </StatNumber>
                  </Stat>
                  <Stat>
                    <StatLabel>Decision Points</StatLabel>
                    <StatNumber color="orange.500">
                      {analysisResults.decision_points?.length || 0}
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

                {/* Conversation Summary */}
                {analysisResults.conversation_summary && (
                  <Grid templateColumns={{ base: '1fr', md: 'repeat(3, 1fr)' }} gap={6}>
                    <Box p={4} bg="green.50" borderRadius="md">
                      <HStack spacing={3} mb={2}>
                        <Icon as={FiUsers} color="green.500" />
                        <Heading size="sm">Participation</Heading>
                      </HStack>
                      <Text fontSize="sm" color="gray.600">
                        Avg: {Math.round(analysisResults.conversation_summary.average_statements_per_speaker)} statements per speaker
                      </Text>
                    </Box>
                    <Box p={4} bg="blue.50" borderRadius="md">
                      <HStack spacing={3} mb={2}>
                        <Icon as={FiHeart} color="blue.500" />
                        <Heading size="sm">Emotional Climate</Heading>
                      </HStack>
                      <Text fontSize="sm" color="gray.600">
                        {analysisResults.conversation_summary.emotional_climate?.dominant_emotion?.replace('_', ' ')}
                      </Text>
                    </Box>
                    <Box p={4} bg="orange.50" borderRadius="md">
                      <HStack spacing={3} mb={2}>
                        <Icon as={FiTarget} color="orange.500" />
                        <Heading size="sm">Decision Making</Heading>
                      </HStack>
                      <Text fontSize="sm" color="gray.600">
                        {analysisResults.conversation_summary.decision_summary?.total_decisions} decisions identified
                      </Text>
                    </Box>
                  </Grid>
                )}

                {/* Recommendations */}
                {analysisResults.recommendations && analysisResults.recommendations.length > 0 && (
                  <Box mt={6}>
                    <Heading size="md" mb={3}>Recommendations</Heading>
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
                    <Tab>Speaker Analysis</Tab>
                    <Tab>Decision Points</Tab>
                    <Tab>Decision Tree</Tab>
                    <Tab>Conversation Flow</Tab>
                  </TabList>

                  <TabPanels>
                    {/* Speaker Analysis Tab */}
                    <TabPanel>
                      {analysisResults.emotional_analysis && Object.keys(analysisResults.emotional_analysis).length > 0 ? (
                        <Grid templateColumns={{ base: '1fr', md: 'repeat(2, 1fr)' }} gap={6}>
                          {Object.entries(analysisResults.emotional_analysis).map(([speaker, data]) => {
                            const emotionalInfo = getEmotionalStateInfo(data.dominant_emotion);
                            const EmotionalIcon = emotionalInfo.icon;
                            
                            return (
                              <Card key={speaker} variant="outline">
                                <CardBody>
                                  <VStack align="stretch" spacing={4}>
                                    <HStack spacing={3}>
                                      <Avatar size="md" name={speaker}>
                                        <AvatarBadge boxSize="1.0em" bg={`${emotionalInfo.color}.500`}>
                                          <Icon as={EmotionalIcon} color="white" boxSize={3} />
                                        </AvatarBadge>
                                      </Avatar>
                                      <Box>
                                        <Text fontWeight="bold">{speaker}</Text>
                                        <Text fontSize="sm" color="gray.600">
                                          {data.total_statements} statements
                                        </Text>
                                      </Box>
                                      <Spacer />
                                      <Button
                                        size="sm"
                                        variant="outline"
                                        leftIcon={<FiEye />}
                                        onClick={() => {
                                          setSelectedSpeaker({ name: speaker, ...data });
                                          onSpeakerModalOpen();
                                        }}
                                      >
                                        Details
                                      </Button>
                                    </HStack>

                                    <Grid templateColumns="repeat(2, 1fr)" gap={3}>
                                      <Box textAlign="center">
                                        <Text fontSize="lg" fontWeight="bold" color={`${emotionalInfo.color}.500`}>
                                          {Math.round((data.engagement_score || 0) * 100)}%
                                        </Text>
                                        <Text fontSize="xs" color="gray.600">Engagement</Text>
                                      </Box>
                                      <Box textAlign="center">
                                        <Text fontSize="lg" fontWeight="bold" color="blue.500">
                                          {Math.round(data.speaking_time_percentage || 0)}%
                                        </Text>
                                        <Text fontSize="xs" color="gray.600">Speaking Time</Text>
                                      </Box>
                                    </Grid>

                                    <HStack spacing={2} justify="center">
                                      {data.emotional_peaks && data.emotional_peaks.length > 0 && (
                                        <Tag colorScheme="green" size="sm">
                                          {data.emotional_peaks.length} Peaks
                                        </Tag>
                                      )}
                                      {data.emotional_lows && data.emotional_lows.length > 0 && (
                                        <Tag colorScheme="red" size="sm">
                                          {data.emotional_lows.length} Lows
                                        </Tag>
                                      )}
                                    </HStack>
                                  </VStack>
                                </CardBody>
                              </Card>
                            );
                          })}
                        </Grid>
                      ) : (
                        <Alert status="info">
                          <AlertIcon />
                          <AlertTitle>No Speaker Data</AlertTitle>
                          <AlertDescription>
                            No speaker analysis data available.
                          </AlertDescription>
                        </Alert>
                      )}
                    </TabPanel>

                    {/* Decision Points Tab */}
                    <TabPanel>
                      {analysisResults.decision_points && analysisResults.decision_points.length > 0 ? (
                        <TableContainer>
                          <Table variant="simple">
                            <Thead>
                              <Tr>
                                <Th>Decision</Th>
                                <Th>Importance</Th>
                                <Th>Consensus</Th>
                                <Th>Participants</Th>
                                <Th>Actions</Th>
                              </Tr>
                            </Thead>
                            <Tbody>
                              {analysisResults.decision_points.map((decision, index) => (
                                <Tr key={index}>
                                  <Td>
                                    <Text fontSize="sm" maxW="300px" isTruncated>
                                      {decision.decision_text}
                                    </Text>
                                  </Td>
                                  <Td>
                                    <Badge 
                                      colorScheme={decision.importance_score > 0.8 ? 'red' : 
                                                 decision.importance_score > 0.6 ? 'orange' : 'yellow'} 
                                      size="sm"
                                    >
                                      {Math.round((decision.importance_score || 0) * 100)}%
                                    </Badge>
                                  </Td>
                                  <Td>
                                    <Badge colorScheme={getConsensusColor(decision.consensus_level)} size="sm">
                                      {decision.consensus_level?.replace('_', ' ')}
                                    </Badge>
                                  </Td>
                                  <Td>
                                    <AvatarGroup size="xs" max={3}>
                                      {decision.participants?.map((participant, idx) => (
                                        <Avatar key={idx} name={participant} />
                                      ))}
                                    </AvatarGroup>
                                  </Td>
                                  <Td>
                                    <Button
                                      size="sm"
                                      variant="outline"
                                      leftIcon={<FiEye />}
                                      onClick={() => {
                                        setSelectedDecision(decision);
                                        onDecisionModalOpen();
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
                          <AlertTitle>No Decision Points</AlertTitle>
                          <AlertDescription>
                            No significant decision points identified in this conversation.
                          </AlertDescription>
                        </Alert>
                      )}
                    </TabPanel>

                    {/* Decision Tree Tab */}
                    <TabPanel>
                      {analysisResults.decision_tree && analysisResults.decision_tree.nodes ? (
                        <Box p={6} bg="gray.50" borderRadius="md" minH="400px">
                          <VStack spacing={4}>
                            <Heading size="md">Decision Tree Visualization</Heading>
                            <Text fontSize="sm" color="gray.600">
                              Interactive decision tree showing conversation flow and emotional context
                            </Text>
                            
                            {/* Simplified tree representation */}
                            <Grid templateColumns="repeat(auto-fit, minmax(200px, 1fr))" gap={4} w="full">
                              {analysisResults.decision_tree.nodes?.slice(0, 6).map((node, index) => (
                                <Box 
                                  key={index}
                                  p={4} 
                                  bg="white" 
                                  borderRadius="md" 
                                  border="1px"
                                  borderColor="gray.200"
                                  textAlign="center"
                                >
                                  <Text fontSize="sm" fontWeight="bold" mb={2}>
                                    {node.type === 'decision' ? 'Decision' : 
                                     node.type === 'emotion' ? 'Emotion' : 'Speaker'}
                                  </Text>
                                  <Text fontSize="xs" color="gray.600" maxH="60px" overflow="hidden">
                                    {node.label?.length > 50 ? 
                                      node.label.substring(0, 50) + '...' : 
                                      node.label}
                                  </Text>
                                </Box>
                              ))}
                            </Grid>

                            <Text fontSize="xs" color="gray.500">
                              Tree structure: Decision points connected by conversation flow
                            </Text>
                          </VStack>
                        </Box>
                      ) : (
                        <Alert status="info">
                          <AlertIcon />
                          <AlertTitle>No Decision Tree</AlertTitle>
                          <AlertDescription>
                            Decision tree visualization not available for this conversation.
                          </AlertDescription>
                        </Alert>
                      )}
                    </TabPanel>

                    {/* Conversation Flow Tab */}
                    <TabPanel>
                      <VStack align="stretch" spacing={6}>
                        {/* Speaker Overview */}
                        <Box>
                          <Heading size="md" mb={4}>Speaker Overview</Heading>
                          <Grid templateColumns="repeat(auto-fit, minmax(250px, 1fr))" gap={4}>
                            {Object.entries(analysisResults.conversation_summary?.speaker_activity || {}).map(([speaker, activity]) => (
                              <Card key={speaker} variant="outline">
                                <CardBody>
                                  <VStack align="stretch" spacing={3}>
                                    <HStack>
                                      <Icon as={FiUser} color="blue.500" />
                                      <Text fontWeight="bold">{speaker}</Text>
                                    </HStack>
                                    <HStack justify="space-between">
                                      <Text fontSize="sm">Statements:</Text>
                                      <Text fontSize="sm" fontWeight="bold">{activity.statements}</Text>
                                    </HStack>
                                    <HStack justify="space-between">
                                      <Text fontSize="sm">Speaking Time:</Text>
                                      <Text fontSize="sm" fontWeight="bold">{Math.round(activity.speaking_time)}%</Text>
                                    </HStack>
                                    <HStack justify="space-between">
                                      <Text fontSize="sm">Engagement:</Text>
                                      <Badge colorScheme={activity.engagement > 0.7 ? 'green' : 'yellow'}>
                                        {Math.round(activity.engagement * 100)}%
                                      </Badge>
                                    </HStack>
                                  </VStack>
                                </CardBody>
                              </Card>
                            ))}
                          </Grid>
                        </Box>

                        {/* Emotional Climate */}
                        <Box>
                          <Heading size="md" mb={4}>Emotional Climate</Heading>
                          <Box p={4} bg="blue.50" borderRadius="md">
                            <Grid templateColumns="repeat(auto-fit, minmax(150px, 1fr))" gap={4}>
                              {Object.entries(analysisResults.conversation_summary?.emotional_climate?.emotion_distribution || {}).map(([emotion, count]) => {
                                const emotionalInfo = getEmotionalStateInfo(emotion);
                                const EmotionalIcon = emotionalInfo.icon;
                                
                                return (
                                  <VStack key={emotion} spacing={2}>
                                    <Icon as={EmotionalIcon} color={`${emotionalInfo.color}.500`} boxSize={6} />
                                    <Text fontSize="lg" fontWeight="bold">{count}</Text>
                                    <Text fontSize="xs" textAlign="center" color="gray.600">
                                      {emotion.replace('_', ' ')}
                                    </Text>
                                  </VStack>
                                );
                              })}
                            </Grid>
                          </Box>
                        </Box>
                      </VStack>
                    </TabPanel>
                  </TabPanels>
                </Tabs>
              </CardBody>
            </Card>
          </>
        )}

        {/* Conversation Insights Dashboard */}
        {conversationInsights && (
          <Card>
            <CardHeader>
              <Heading size="lg">Conversation Insights</Heading>
              <Text color="gray.600">Historical analysis and patterns</Text>
            </CardHeader>
            <CardBody>
              <Grid templateColumns={{ base: '1fr', md: 'repeat(4, 1fr)' }} gap={6}>
                <Stat>
                  <StatLabel>Total Sessions</StatLabel>
                  <StatNumber color="blue.500">
                    {conversationInsights.overview?.total_sessions || 0}
                  </StatNumber>
                </Stat>
                <Stat>
                  <StatLabel>Speakers Analyzed</StatLabel>
                  <StatNumber color="purple.500">
                    {conversationInsights.overview?.total_speakers_analyzed || 0}
                  </StatNumber>
                </Stat>
                <Stat>
                  <StatLabel>Decisions Found</StatLabel>
                  <StatNumber color="orange.500">
                    {conversationInsights.overview?.total_decisions_identified || 0}
                  </StatNumber>
                </Stat>
                <Stat>
                  <StatLabel>Avg Engagement</StatLabel>
                  <StatNumber color="green.500">
                    {Math.round((conversationInsights.overview?.average_engagement_score || 0) * 100)}%
                  </StatNumber>
                </Stat>
              </Grid>

              <Divider my={6} />

              {/* High Engagement Speakers */}
              {conversationInsights.high_engagement_speakers && conversationInsights.high_engagement_speakers.length > 0 && (
                <Box>
                  <Heading size="md" mb={3}>Most Engaged Speakers</Heading>
                  <Wrap>
                    {conversationInsights.high_engagement_speakers.slice(0, 5).map((speaker, index) => (
                      <WrapItem key={index}>
                        <Tag colorScheme="green" size="lg">
                          <TagLabel>{speaker.name} ({Math.round(speaker.engagement_score * 100)}%)</TagLabel>
                        </Tag>
                      </WrapItem>
                    ))}
                  </Wrap>
                </Box>
              )}
            </CardBody>
          </Card>
        )}

        {/* Modals */}
        <SpeakerProfileModal 
          speaker={selectedSpeaker} 
          isOpen={isSpeakerModalOpen} 
          onClose={() => {
            onSpeakerModalClose();
            setSelectedSpeaker(null);
          }} 
        />

        <DecisionPointModal 
          decision={selectedDecision} 
          isOpen={isDecisionModalOpen} 
          onClose={() => {
            onDecisionModalClose();
            setSelectedDecision(null);
          }} 
        />
      </VStack>
    </Container>
  );
};

export default LiveConversationAnalyst;