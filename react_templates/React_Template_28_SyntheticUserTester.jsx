/**
 * Template #28: Synthetic User Tester - React Frontend
 * Advanced AI-powered website screenshot analysis and user persona generation interface
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
  Avatar,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  StatArrow,
  Image,
  Input,
  Textarea,
  Select,
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
  TagLeftIcon,
  Wrap,
  WrapItem,
  IconButton
} from '@chakra-ui/react';
import {
  FaUpload,
  FaUser,
  FaChartLine,
  FaEye,
  FaDownload,
  FaShare,
  FaFilter,
  FaSearch,
  FaRobot,
  FaBrain,
  FaRoute,
  FaUsers,
  FaLightbulb,
  FaExclamationTriangle,
  FaCheckCircle,
  FaTimesCircle,
  FaInfoCircle,
  FaFileImage,
  FaCamera,
  FaMagic,
  FaChartBar,
  FaHeart,
  FaComment,
  FaStar,
  FaClock,
  FaGlobe
} from 'react-icons/fa';
import { SiOpenai } from 'react-icons/si';

// Color mode values
const bgColor = useColorModeValue('gray.50', 'gray.900');
const cardBg = useColorModeValue('white', 'gray.800');
const borderColor = useColorModeValue('gray.200', 'gray.600');

// Types
interface Demographics {
  age_range: string;
  location: string;
  education: string;
  income: string;
}

interface Psychographics {
  personality: string[];
  values: string[];
  frustrations: string[];
  goals: string[];
}

interface JourneyStep {
  step: number;
  action: string;
  thoughts: string;
  emotions: string;
  pain_points: string;
}

interface Persona {
  id: string;
  name: string;
  demographics: Demographics;
  psychographics: Psychographics;
  success_prediction: string;
  journey_steps: JourneyStep[];
}

interface AnalysisResult {
  analysis_id: string;
  personas: Persona[];
  overall_success_rate: number;
  timestamp: string;
}

// Mock data for demonstration
const mockPersonas: Persona[] = [
  {
    id: '1',
    name: 'Alex Chen',
    demographics: {
      age_range: '25-35',
      location: 'Urban metropolitan areas',
      education: "Bachelor's degree",
      income: '$50,000 - $80,000'
    },
    psychographics: {
      personality: ['fast-paced', 'goal-oriented', 'value efficiency'],
      values: ['Efficiency', 'Career growth', 'Modern technology'],
      frustrations: ['slow loading', 'complicated navigation', 'poor mobile experience'],
      goals: ['quick information', 'easy transactions', 'modern design']
    },
    success_prediction: 'High success probability (85%) - Website aligns well with user expectations and goals',
    journey_steps: [
      {
        step: 1,
        action: 'Initial page load and first impression',
        thoughts: 'How does this first glance align with Alex Chen\'s expectations?',
        emotions: 'Curiosity',
        pain_points: 'None yet - first impressions'
      },
      {
        step: 2,
        action: 'Navigation and information seeking',
        thoughts: 'Can Alex Chen quickly find what they\'re looking for?',
        emotions: 'Determination',
        pain_points: 'Standard navigation challenges'
      },
      {
        step: 3,
        action: 'Content engagement and evaluation',
        thoughts: 'Does the content resonate with Alex Chen\'s values?',
        emotions: 'Focused',
        pain_points: 'Standard content challenges'
      },
      {
        step: 4,
        action: 'Action or conversion attempt',
        thoughts: 'Will Alex Chen complete the desired action?',
        emotions: 'Decision-making',
        pain_points: 'Standard conversion challenges'
      },
      {
        step: 5,
        action: 'Completion or abandonment',
        thoughts: 'What factors influenced Alex Chen\'s final decision?',
        emotions: 'Satisfaction',
        pain_points: 'Final obstacles or successful completion'
      }
    ]
  },
  {
    id: '2',
    name: 'Jordan Rodriguez',
    demographics: {
      age_range: '18-24',
      location: 'Urban areas',
      education: 'In college or recent graduate',
      income: '$20,000 - $40,000'
    },
    psychographics: {
      personality: ['mobile-first', 'visual-focused', 'short attention span'],
      values: ['Authenticity', 'Social responsibility', 'Innovation'],
      frustrations: ['desktop-only features', 'slow performance', 'boring visuals'],
      goals: ['instant gratification', 'social sharing', 'trendy design']
    },
    success_prediction: 'Moderate success probability (72%) - Website has good potential but may face some challenges',
    journey_steps: [
      {
        step: 1,
        action: 'Initial page load and first impression',
        thoughts: 'How does this first glance align with Jordan Rodriguez\'s expectations?',
        emotions: 'Curiosity',
        pain_points: 'None yet - first impressions'
      },
      {
        step: 2,
        action: 'Navigation and information seeking',
        thoughts: 'Can Jordan Rodriguez quickly find what they\'re looking for?',
        emotions: 'Determination',
        pain_points: 'Complex menu structure, unclear navigation labels'
      },
      {
        step: 3,
        action: 'Content engagement and evaluation',
        thoughts: 'Does the content resonate with Jordan Rodriguez\'s values?',
        emotions: 'Interest',
        pain_points: 'Standard content challenges'
      },
      {
        step: 4,
        action: 'Action or conversion attempt',
        thoughts: 'Will Jordan Rodriguez complete the desired action?',
        emotions: 'Decision-making',
        pain_points: 'Unclear call-to-action, missing conversion elements'
      },
      {
        step: 5,
        action: 'Completion or abandonment',
        thoughts: 'What factors influenced Jordan Rodriguez\'s final decision?',
        emotions: 'Uncertainty',
        pain_points: 'Final obstacles or successful completion'
      }
    ]
  }
];

const App: React.FC = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);
  const [selectedPersona, setSelectedPersona] = useState<Persona | null>(null);
  const [filterPersona, setFilterPersona] = useState<string>('all');
  const [searchTerm, setSearchTerm] = useState('');
  const { isOpen, onOpen, onClose } = useDisclosure();
  const toast = useToast();

  // Event handlers
  const handleFileSelect = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      // Validate file type
      if (!file.type.startsWith('image/')) {
        toast({
          title: 'Invalid file type',
          description: 'Please select an image file (PNG, JPG, GIF)',
          status: 'error',
          duration: 5000,
          isClosable: true,
        });
        return;
      }

      // Validate file size (max 10MB)
      if (file.size > 10 * 1024 * 1024) {
        toast({
          title: 'File too large',
          description: 'Please select an image smaller than 10MB',
          status: 'error',
          duration: 5000,
          isClosable: true,
        });
        return;
      }

      setSelectedFile(file);

      // Create preview
      const reader = new FileReader();
      reader.onload = (e) => {
        setImagePreview(e.target?.result as string);
      };
      reader.readAsDataURL(file);
    }
  }, [toast]);

  const handleAnalyze = useCallback(async () => {
    if (!selectedFile && !imagePreview) {
      toast({
        title: 'No image selected',
        description: 'Please upload a website screenshot to analyze',
        status: 'warning',
        duration: 5000,
        isClosable: true,
      });
      return;
    }

    setIsAnalyzing(true);

    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 3000));

      const mockResult: AnalysisResult = {
        analysis_id: `analysis_${Date.now()}`,
        personas: mockPersonas,
        overall_success_rate: 78.5,
        timestamp: new Date().toISOString()
      };

      setAnalysisResult(mockResult);

      toast({
        title: 'Analysis Complete!',
        description: 'User personas and journey predictions have been generated',
        status: 'success',
        duration: 5000,
        isClosable: true,
      });

    } catch (error) {
      toast({
        title: 'Analysis Failed',
        description: 'Failed to analyze the screenshot. Please try again.',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setIsAnalyzing(false);
    }
  }, [selectedFile, imagePreview, toast]);

  const getSuccessRateColor = (rate: number) => {
    if (rate >= 80) return 'green';
    if (rate >= 60) return 'yellow';
    if (rate >= 40) return 'orange';
    return 'red';
  };

  const getSuccessRateIcon = (rate: number) => {
    if (rate >= 80) return FaCheckCircle;
    if (rate >= 60) return FaInfoCircle;
    if (rate >= 40) return FaExclamationTriangle;
    return FaTimesCircle;
  };

  const filteredPersonas = analysisResult?.personas.filter(persona => {
    const matchesFilter = filterPersona === 'all' || 
      (filterPersona === 'high' && persona.success_prediction.includes('High')) ||
      (filterPersona === 'moderate' && persona.success_prediction.includes('Moderate')) ||
      (filterPersona === 'low' && persona.success_prediction.includes('Low'));
    
    const matchesSearch = searchTerm === '' || 
      persona.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      persona.demographics.age_range.includes(searchTerm) ||
      persona.psychographics.personality.some(p => p.toLowerCase().includes(searchTerm.toLowerCase()));
    
    return matchesFilter && matchesSearch;
  }) || [];

  const extractSuccessRate = (prediction: string): number => {
    const match = prediction.match(/\((\d+)%\)/);
    return match ? parseInt(match[1]) : 0;
  };

  return (
    <Box bg={bgColor} minH="100vh">
      <Container maxW="7xl" py={8}>
        {/* Header */}
        <VStack spacing={6} align="stretch">
          <Box textAlign="center">
            <HStack justify="center" spacing={4} mb={4}>
              <Icon as={FaRobot} boxSize={8} color="blue.500" />
              <Heading size="2xl" bgGradient="linear(to-r, blue.400, purple.500)" bgClip="text">
                Synthetic User Tester
              </Heading>
              <Icon as={FaBrain} boxSize={8} color="purple.500" />
            </HStack>
            <Text fontSize="xl" color="gray.600">
              AI-powered website screenshot analysis and user persona generation
            </Text>
          </Box>

          {/* Upload Section */}
          <Card bg={cardBg} borderWidth="1px" borderColor={borderColor}>
            <CardHeader>
              <HStack>
                <Icon as={FaUpload} color="blue.500" />
                <Heading size="md">Upload Website Screenshot</Heading>
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
                    accept="image/*"
                    onChange={handleFileSelect}
                    display="none"
                    id="file-upload"
                  />
                  <label htmlFor="file-upload" style={{ cursor: 'pointer' }}>
                    <VStack spacing={4}>
                      <Icon as={FaFileImage} boxSize={12} color="gray.400" />
                      <Text fontSize="lg" fontWeight="medium">
                        Click to upload website screenshot
                      </Text>
                      <Text fontSize="sm" color="gray.500">
                        PNG, JPG, GIF up to 10MB
                      </Text>
                      <Button colorScheme="blue" leftIcon={<FaUpload />}>
                        Choose File
                      </Button>
                    </VStack>
                  </label>
                </Box>

                {imagePreview && (
                  <Box w="full">
                    <Text fontWeight="medium" mb={2}>Preview:</Text>
                    <Image
                      src={imagePreview}
                      alt="Website screenshot preview"
                      maxH="300px"
                      objectFit="contain"
                      borderRadius="md"
                      borderWidth="1px"
                      borderColor={borderColor}
                    />
                  </Box>
                )}

                <Button
                  colorScheme="blue"
                  size="lg"
                  leftIcon={isAnalyzing ? <Spinner size="sm" /> : <FaMagic />}
                  onClick={handleAnalyze}
                  isLoading={isAnalyzing}
                  loadingText="Analyzing..."
                  isDisabled={!selectedFile && !imagePreview}
                >
                  Analyze Website
                </Button>
              </VStack>
            </CardBody>
          </Card>

          {/* Results Section */}
          {analysisResult && (
            <VStack spacing={6} align="stretch">
              {/* Overall Statistics */}
              <Card bg={cardBg} borderWidth="1px" borderColor={borderColor}>
                <CardHeader>
                  <HStack>
                    <Icon as={FaChartBar} color="green.500" />
                    <Heading size="md">Analysis Overview</Heading>
                  </HStack>
                </CardHeader>
                <CardBody>
                  <Grid templateColumns="repeat(auto-fit, minmax(200px, 1fr))" gap={6}>
                    <Stat>
                      <StatLabel>Overall Success Rate</StatLabel>
                      <StatNumber color={`${getSuccessRateColor(analysisResult.overall_success_rate)}.500`}>
                        {analysisResult.overall_success_rate.toFixed(1)}%
                      </StatNumber>
                      <StatHelpText>
                        <StatArrow type="increase" />
                        Average across all personas
                      </StatHelpText>
                    </Stat>
                    <Stat>
                      <StatLabel>Personas Generated</StatLabel>
                      <StatNumber>{analysisResult.personas.length}</StatNumber>
                      <StatHelpText>
                        <Icon as={FaUsers} mr={1} />
                        Unique user types
                      </StatHelpText>
                    </Stat>
                    <Stat>
                      <StatLabel>High Success Rate</StatLabel>
                      <StatNumber color="green.500">
                        {analysisResult.personas.filter(p => extractSuccessRate(p.success_prediction) >= 80).length}
                      </StatNumber>
                      <StatHelpText>
                        Personas with 80%+ success
                      </StatHelpText>
                    </Stat>
                    <Stat>
                      <StatLabel>Analysis ID</StatLabel>
                      <StatNumber fontSize="md" fontFamily="mono">
                        {analysisResult.analysis_id.slice(0, 8)}...
                      </StatNumber>
                      <StatHelpText>
                        <Icon as={FaClock} mr={1} />
                        {new Date(analysisResult.timestamp).toLocaleString()}
                      </StatHelpText>
                    </Stat>
                  </Grid>
                </CardBody>
              </Card>

              {/* Filters and Search */}
              <Card bg={cardBg} borderWidth="1px" borderColor={borderColor}>
                <CardBody>
                  <HStack spacing={4} flexWrap="wrap">
                    <Box>
                      <Text fontSize="sm" fontWeight="medium" mb={1}>Filter by Success Rate:</Text>
                      <Select
                        value={filterPersona}
                        onChange={(e) => setFilterPersona(e.target.value)}
                        size="sm"
                        w="200px"
                      >
                        <option value="all">All Personas</option>
                        <option value="high">High Success (80%+)</option>
                        <option value="moderate">Moderate Success (60-79%)</option>
                        <option value="low">Low Success (&lt;60%)</option>
                      </Select>
                    </Box>
                    <Box>
                      <Text fontSize="sm" fontWeight="medium" mb={1}>Search Personas:</Text>
                      <Input
                        placeholder="Search by name, age, or traits..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        size="sm"
                        w="250px"
                        leftElement={<Icon as={FaSearch} color="gray.400" />}
                      />
                    </Box>
                  </HStack>
                </CardBody>
              </Card>

              {/* Personas Grid */}
              <Grid templateColumns="repeat(auto-fill, minmax(400px, 1fr))" gap={6}>
                {filteredPersonas.map((persona) => {
                  const successRate = extractSuccessRate(persona.success_prediction);
                  const SuccessIcon = getSuccessRateIcon(successRate);
                  
                  return (
                    <Card
                      key={persona.id}
                      bg={cardBg}
                      borderWidth="1px"
                      borderColor={borderColor}
                      cursor="pointer"
                      transition="all 0.3s"
                      _hover={{
                        transform: 'translateY(-2px)',
                        shadow: 'lg',
                        borderColor: 'blue.300'
                      }}
                      onClick={() => {
                        setSelectedPersona(persona);
                        onOpen();
                      }}
                    >
                      <CardHeader>
                        <HStack justify="space-between">
                          <HStack>
                            <Avatar name={persona.name} size="md" />
                            <VStack align="start" spacing={1}>
                              <Heading size="sm">{persona.name}</Heading>
                              <Text fontSize="xs" color="gray.500">
                                {persona.demographics.age_range} • {persona.demographics.location}
                              </Text>
                            </VStack>
                          </HStack>
                          <VStack align="end" spacing={1}>
                            <Icon as={SuccessIcon} color={`${getSuccessRateColor(successRate)}.500`} />
                            <Text fontSize="sm" fontWeight="bold" color={`${getSuccessRateColor(successRate)}.500`}>
                              {successRate}%
                            </Text>
                          </VStack>
                        </HStack>
                      </CardHeader>
                      <CardBody pt={0}>
                        <VStack align="stretch" spacing={3}>
                          <Box>
                            <Text fontSize="sm" fontWeight="medium" mb={1}>Personality:</Text>
                            <Wrap>
                              {persona.psychographics.personality.slice(0, 3).map((trait, index) => (
                                <WrapItem key={index}>
                                  <Tag size="sm" colorScheme="blue" variant="subtle">
                                    <TagLabel>{trait}</TagLabel>
                                  </Tag>
                                </WrapItem>
                              ))}
                            </Wrap>
                          </Box>
                          
                          <Box>
                            <Text fontSize="sm" fontWeight="medium" mb={1}>Top Frustrations:</Text>
                            <Wrap>
                              {persona.psychographics.frustrations.slice(0, 2).map((frustration, index) => (
                                <WrapItem key={index}>
                                  <Tag size="sm" colorScheme="red" variant="subtle">
                                    <TagLabel>{frustration}</TagLabel>
                                  </Tag>
                                </WrapItem>
                              ))}
                            </Wrap>
                          </Box>

                          <Progress
                            value={successRate}
                            colorScheme={getSuccessRateColor(successRate)}
                            size="sm"
                            borderRadius="full"
                          />
                          
                          <Text fontSize="xs" color="gray.600" noOfLines={2}>
                            {persona.success_prediction}
                          </Text>
                        </VStack>
                      </CardBody>
                    </Card>
                  );
                })}
              </Grid>

              {filteredPersonas.length === 0 && (
                <Alert status="info">
                  <AlertIcon />
                  <AlertTitle>No personas match your filters</AlertTitle>
                  <AlertDescription>
                    Try adjusting your filter or search criteria to see more results.
                  </AlertDescription>
                </Alert>
              )}
            </VStack>
          )}
        </VStack>
      </Container>

      {/* Persona Detail Modal */}
      <Modal isOpen={isOpen} onClose={onClose} size="6xl">
        <ModalOverlay />
        <ModalContent maxH="90vh" overflow="hidden">
          <ModalHeader>
            <HStack>
              <Icon as={FaUser} color="blue.500" />
              <Text>Persona Details: {selectedPersona?.name}</Text>
            </HStack>
          </ModalHeader>
          <ModalCloseButton />
          <ModalBody overflowY="auto">
            {selectedPersona && (
              <Tabs variant="enclosed">
                <TabList>
                  <Tab><Icon as={FaUser} mr={2} />Profile</Tab>
                  <Tab><Icon as={FaRoute} mr={2} />User Journey</Tab>
                  <Tab><Icon as={FaChartLine} mr={2} />Analysis</Tab>
                </TabList>

                <TabPanels>
                  {/* Profile Tab */}
                  <TabPanel>
                    <Grid templateColumns="repeat(auto-fit, minmax(300px, 1fr))" gap={6}>
                      <Card bg={cardBg} borderWidth="1px" borderColor={borderColor}>
                        <CardHeader>
                          <Heading size="sm">Demographics</Heading>
                        </CardHeader>
                        <CardBody>
                          <VStack align="stretch" spacing={3}>
                            <HStack justify="space-between">
                              <Text fontWeight="medium">Age Range:</Text>
                              <Badge>{selectedPersona.demographics.age_range}</Badge>
                            </HStack>
                            <HStack justify="space-between">
                              <Text fontWeight="medium">Location:</Text>
                              <Badge>{selectedPersona.demographics.location}</Badge>
                            </HStack>
                            <HStack justify="space-between">
                              <Text fontWeight="medium">Education:</Text>
                              <Badge>{selectedPersona.demographics.education}</Badge>
                            </HStack>
                            <HStack justify="space-between">
                              <Text fontWeight="medium">Income:</Text>
                              <Badge>{selectedPersona.demographics.income}</Badge>
                            </HStack>
                          </VStack>
                        </CardBody>
                      </Card>

                      <Card bg={cardBg} borderWidth="1px" borderColor={borderColor}>
                        <CardHeader>
                          <Heading size="sm">Psychographics</Heading>
                        </CardHeader>
                        <CardBody>
                          <VStack align="stretch" spacing={4}>
                            <Box>
                              <Text fontWeight="medium" mb={2}>Personality Traits:</Text>
                              <Wrap>
                                {selectedPersona.psychographics.personality.map((trait, index) => (
                                  <WrapItem key={index}>
                                    <Tag colorScheme="blue" variant="subtle">
                                      <TagLabel>{trait}</TagLabel>
                                    </Tag>
                                  </WrapItem>
                                ))}
                              </Wrap>
                            </Box>
                            
                            <Box>
                              <Text fontWeight="medium" mb={2}>Core Values:</Text>
                              <Wrap>
                                {selectedPersona.psychographics.values.map((value, index) => (
                                  <WrapItem key={index}>
                                    <Tag colorScheme="green" variant="subtle">
                                      <TagLabel>{value}</TagLabel>
                                    </Tag>
                                  </WrapItem>
                                ))}
                              </Wrap>
                            </Box>
                          </VStack>
                        </CardBody>
                      </Card>
                    </Grid>

                    <Grid templateColumns="repeat(auto-fit, minmax(300px, 1fr))" gap={6} mt={6}>
                      <Card bg={cardBg} borderWidth="1px" borderColor={borderColor}>
                        <CardHeader>
                          <Heading size="sm">Goals & Motivations</Heading>
                        </CardHeader>
                        <CardBody>
                          <VStack align="stretch" spacing={2}>
                            {selectedPersona.psychographics.goals.map((goal, index) => (
                              <HStack key={index}>
                                <Icon as={FaLightbulb} color="yellow.500" />
                                <Text>{goal}</Text>
                              </HStack>
                            ))}
                          </VStack>
                        </CardBody>
                      </Card>

                      <Card bg={cardBg} borderWidth="1px" borderColor={borderColor}>
                        <CardHeader>
                          <Heading size="sm">Frustrations & Pain Points</Heading>
                        </CardHeader>
                        <CardBody>
                          <VStack align="stretch" spacing={2}>
                            {selectedPersona.psychographics.frustrations.map((frustration, index) => (
                              <HStack key={index}>
                                <Icon as={FaExclamationTriangle} color="red.500" />
                                <Text>{frustration}</Text>
                              </HStack>
                            ))}
                          </VStack>
                        </CardBody>
                      </Card>
                    </Grid>
                  </TabPanel>

                  {/* User Journey Tab */}
                  <TabPanel>
                    <VStack align="stretch" spacing={4}>
                      {selectedPersona.journey_steps.map((step, index) => (
                        <Card key={index} bg={cardBg} borderWidth="1px" borderColor={borderColor}>
                          <CardBody>
                            <VStack align="stretch" spacing={4}>
                              <HStack justify="space-between">
                                <HStack>
                                  <Box
                                    bg="blue.500"
                                    color="white"
                                    borderRadius="full"
                                    w={8}
                                    h={8}
                                    display="flex"
                                    alignItems="center"
                                    justifyContent="center"
                                    fontWeight="bold"
                                  >
                                    {step.step}
                                  </Box>
                                  <Heading size="sm">{step.action}</Heading>
                                </HStack>
                                <Badge colorScheme="blue" variant="subtle">
                                  {step.emotions}
                                </Badge>
                              </HStack>
                              
                              <Box>
                                <Text fontWeight="medium" mb={1}>User Thoughts:</Text>
                                <Text fontSize="sm" color="gray.600" fontStyle="italic">
                                  "{step.thoughts}"
                                </Text>
                              </Box>
                              
                              <Box>
                                <Text fontWeight="medium" mb={1}>Potential Pain Points:</Text>
                                <Text fontSize="sm" color="red.600">
                                  {step.pain_points}
                                </Text>
                              </Box>
                            </VStack>
                          </CardBody>
                        </Card>
                      ))}
                    </VStack>
                  </TabPanel>

                  {/* Analysis Tab */}
                  <TabPanel>
                    <Card bg={cardBg} borderWidth="1px" borderColor={borderColor}>
                      <CardHeader>
                        <Heading size="sm">Success Prediction</Heading>
                      </CardHeader>
                      <CardBody>
                        <VStack align="stretch" spacing={4}>
                          <Box>
                            <HStack justify="space-between" mb={2}>
                              <Text fontWeight="medium">Success Probability</Text>
                              <Text fontWeight="bold" fontSize="lg" color={`${getSuccessRateColor(extractSuccessRate(selectedPersona.success_prediction))}.500`}>
                                {extractSuccessRate(selectedPersona.success_prediction)}%
                              </Text>
                            </HStack>
                            <Progress
                              value={extractSuccessRate(selectedPersona.success_prediction)}
                              colorScheme={getSuccessRateColor(extractSuccessRate(selectedPersona.success_prediction))}
                              size="lg"
                              borderRadius="full"
                            />
                          </Box>
                          
                          <Box>
                            <Text fontWeight="medium" mb={2}>Analysis Summary:</Text>
                            <Text color="gray.600">
                              {selectedPersona.success_prediction}
                            </Text>
                          </Box>

                          <Divider />

                          <Grid templateColumns="repeat(auto-fit, minmax(200px, 1fr))" gap={4}>
                            <Stat>
                              <StatLabel>Journey Steps</StatLabel>
                              <StatNumber>{selectedPersona.journey_steps.length}</StatNumber>
                              <StatHelpText>User interaction points</StatHelpText>
                            </Stat>
                            <Stat>
                              <StatLabel>Pain Points</StatLabel>
                              <StatNumber>{selectedPersona.psychographics.frustrations.length}</StatNumber>
                              <StatHelpText>Identified challenges</StatHelpText>
                            </Stat>
                            <Stat>
                              <StatLabel>Success Factors</StatLabel>
                              <StatNumber>{selectedPersona.psychographics.goals.length}</StatNumber>
                              <StatHelpText>User motivations</StatHelpText>
                            </Stat>
                          </Grid>
                        </VStack>
                      </CardBody>
                    </Card>
                  </TabPanel>
                </TabPanels>
              </Tabs>
            )}
          </ModalBody>
          <ModalFooter>
            <HStack spacing={3}>
              <Button
                leftIcon={<FaDownload />}
                colorScheme="blue"
                variant="outline"
                onClick={() => {
                  // Export functionality would go here
                  toast({
                    title: 'Export Started',
                    description: 'Persona data is being prepared for download',
                    status: 'info',
                    duration: 3000,
                    isClosable: true,
                  });
                }}
              >
                Export Data
              </Button>
              <Button leftIcon={<FaShare />} colorScheme="green" variant="outline">
                Share Results
              </Button>
              <Button onClick={onClose}>Close</Button>
            </HStack>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </Box>
  );
};

export default App;
