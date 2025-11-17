/**
 * Template #32: Real-Time Traffic Predictor
 * React frontend for traffic prediction with real-time data and historical analysis
 */

import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Container,
  VStack,
  HStack,
  Heading,
  Text,
  Button,
  Input,
  Select,
  Card,
  CardHeader,
  CardBody,
  Grid,
  GridItem,
  Badge,
  Progress,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  Divider,
  useToast,
  FormControl,
  FormLabel,
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
  Tooltip
} from '@chakra-ui/react';
import {
  FiNavigation,
  FiClock,
  FiTrendingUp,
  FiMapPin,
  FiCloud,
  FiAlertTriangle,
  FiRefreshCw,
  FiEye,
  FiCalendar,
  FiActivity,
  FiTarget,
  FiSun,
  FiCloudRain,
  FiSnow,
  FiZap
} from 'react-icons/fi';

// API Configuration
const API_BASE_URL = 'http://localhost:8000';

const RealTimeTrafficPredictor = () => {
  const [origin, setOrigin] = useState('');
  const [destination, setDestination] = useState('');
  const [predictionTime, setPredictionTime] = useState('');
  const [routePreference, setRoutePreference] = useState('fastest');
  const [isPredicting, setIsPredicting] = useState(false);
  const [prediction, setPrediction] = useState(null);
  const [locations, setLocations] = useState([]);
  const [currentConditions, setCurrentConditions] = useState(null);
  const [recentPredictions, setRecentPredictions] = useState([]);
  const [historicalData, setHistoricalData] = useState(null);
  const [activeTab, setActiveTab] = useState(0);
  const { isOpen: isDetailsModalOpen, onOpen: onDetailsModalOpen, onClose: onDetailsModalClose } = useDisclosure();
  const toast = useToast();

  // Load available locations on component mount
  useEffect(() => {
    loadLocations();
    loadRecentPredictions();
    
    // Set default prediction time (2 hours from now)
    const defaultTime = new Date();
    defaultTime.setHours(defaultTime.getHours() + 2);
    setPredictionTime(defaultTime.toISOString().slice(0, 16));
  }, []);

  // Load available locations
  const loadLocations = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/locations`);
      if (response.ok) {
        const data = await response.json();
        setLocations(data.locations);
      }
    } catch (error) {
      console.error('Error loading locations:', error);
    }
  }, []);

  // Load recent predictions
  const loadRecentPredictions = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/predictions?limit=5`);
      if (response.ok) {
        const data = await response.json();
        setRecentPredictions(data.predictions);
      }
    } catch (error) {
      console.error('Error loading recent predictions:', error);
    }
  }, []);

  // Generate traffic prediction
  const generatePrediction = useCallback(async () => {
    if (!origin || !destination || !predictionTime) {
      toast({
        title: 'Missing Information',
        description: 'Please fill in all required fields',
        status: 'warning',
        duration: 3000,
        isClosable: true,
      });
      return;
    }

    if (origin === destination) {
      toast({
        title: 'Invalid Route',
        description: 'Origin and destination cannot be the same',
        status: 'warning',
        duration: 3000,
        isClosable: true,
      });
      return;
    }

    setIsPredicting(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/predict-traffic`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
          origin,
          destination,
          prediction_time: predictionTime,
          route_preference: routePreference
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Prediction failed');
      }

      const result = await response.json();
      setPrediction(result);
      loadHistoricalData(origin, destination);
      loadRecentPredictions();

      toast({
        title: 'Prediction Generated',
        description: `Traffic prediction completed with ${Math.round(result.confidence_score * 100)}% confidence`,
        status: 'success',
        duration: 5000,
        isClosable: true,
      });

    } catch (error) {
      console.error('Error generating prediction:', error);
      toast({
        title: 'Prediction Failed',
        description: error.message || 'Failed to generate traffic prediction',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setIsPredicting(false);
    }
  }, [origin, destination, predictionTime, routePreference]);

  // Load historical data for route
  const loadHistoricalData = useCallback(async (origin, destination) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/historical/${origin}/${destination}`);
      if (response.ok) {
        const data = await response.json();
        setHistoricalData(data);
      }
    } catch (error) {
      console.error('Error loading historical data:', error);
    }
  }, []);

  // Load current traffic conditions
  const loadCurrentConditions = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/traffic-conditions`);
      if (response.ok) {
        const data = await response.json();
        setCurrentConditions(data);
      }
    } catch (error) {
      console.error('Error loading traffic conditions:', error);
    }
  }, []);

  // Get weather icon component
  const getWeatherIcon = (weather) => {
    const iconProps = { boxSize: 6 };
    switch (weather) {
      case 'clear':
        return <Icon as={FiSun} color="yellow.500" {...iconProps} />;
      case 'rain':
        return <Icon as={FiCloudRain} color="blue.500" {...iconProps} />;
      case 'snow':
        return <Icon as={FiSnow} color="blue.300" {...iconProps} />;
      case 'storm':
        return <Icon as={FiZap} color="purple.500" {...iconProps} />;
      default:
        return <Icon as={FiCloud} color="gray.500" {...iconProps} />;
    }
  };

  // Get congestion level color
  const getCongestionColor = (level) => {
    switch (level) {
      case 'low':
        return 'green';
      case 'moderate':
        return 'yellow';
      case 'high':
        return 'orange';
      case 'severe':
        return 'red';
      default:
        return 'gray';
    }
  };

  // Confidence score component
  const ConfidenceScore = ({ score }) => {
    const getScoreColor = (score) => {
      if (score >= 0.85) return 'green';
      if (score >= 0.70) return 'yellow';
      return 'red';
    };

    const getScoreLabel = (score) => {
      if (score >= 0.85) return 'High';
      if (score >= 0.70) return 'Moderate';
      return 'Low';
    };

    return (
      <Stat>
        <StatLabel>Confidence Score</StatLabel>
        <StatNumber color={`${getScoreColor(score)}.500`}>
          {Math.round(score * 100)}%
        </StatNumber>
        <StatHelpText>
          <Badge colorScheme={getScoreColor(score)} size="sm">
            {getScoreLabel(score)} Confidence
          </Badge>
        </StatHelpText>
      </Stat>
    );
  };

  // Traffic conditions table component
  const TrafficConditionsTable = ({ conditions }) => {
    if (!conditions || !conditions.conditions) return null;

    return (
      <TableContainer>
        <Table variant="simple" size="sm">
          <Thead>
            <Tr>
              <Th>Route</Th>
              <Th>Congestion</Th>
              <Th>Avg Speed</Th>
              <Th>Weather</Th>
              <Th>Incidents</Th>
            </Tr>
          </Thead>
          <Tbody>
            {conditions.conditions.slice(0, 10).map((condition, index) => (
              <Tr key={index}>
                <Td>
                  <Text fontSize="sm" fontWeight="medium">
                    {condition.location}
                  </Text>
                </Td>
                <Td>
                  <Badge colorScheme={getCongestionColor(condition.congestion_level)} size="sm">
                    {condition.congestion_level}
                  </Badge>
                </Td>
                <Td>
                  <Text fontSize="sm">
                    {Math.round(condition.average_speed)} km/h
                  </Text>
                </Td>
                <Td>
                  <HStack spacing={1}>
                    {getWeatherIcon(condition.weather)}
                    <Text fontSize="sm" textTransform="capitalize">
                      {condition.weather}
                    </Text>
                  </HStack>
                </Td>
                <Td>
                  <Badge colorScheme={condition.incidents > 0 ? 'red' : 'green'} size="sm">
                    {condition.incidents}
                  </Badge>
                </Td>
              </Tr>
            ))}
          </Tbody>
        </Table>
      </TableContainer>
    );
  };

  // Historical data visualization
  const HistoricalDataVisualization = ({ data }) => {
    if (!data || !data.data_points) return null;

    const peakHours = data.data_points
      .filter(point => point.peak_factor > 1.2)
      .sort((a, b) => b.peak_factor - a.peak_factor)
      .slice(0, 5);

    return (
      <VStack align="stretch" spacing={4}>
        <Box>
          <Heading size="md" mb={3}>Peak Traffic Hours</Heading>
          <Wrap>
            {peakHours.map((point, index) => (
              <WrapItem key={index}>
                <Tag colorScheme="red" size="lg">
                  <TagLabel>
                    {['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'][point.day_of_week]} {point.hour}:00
                    {' '}({Math.round(point.avg_duration)}min)
                  </TagLabel>
                </Tag>
              </WrapItem>
            ))}
          </Wrap>
        </Box>

        <Divider />

        <Box>
          <Heading size="md" mb={3}>Statistical Summary</Heading>
          <Grid templateColumns="repeat(3, 1fr)" gap={4}>
            <Stat>
              <StatLabel>Average Duration</StatLabel>
              <StatNumber>
                {Math.round(data.data_points.reduce((sum, p) => sum + p.avg_duration, 0) / data.data_points.length)} min
              </StatNumber>
            </Stat>
            <Stat>
              <StatLabel>Peak Factor</StatLabel>
              <StatNumber>
                {Math.round((data.data_points.reduce((sum, p) => sum + p.peak_factor, 0) / data.data_points.length) * 100) / 100}x
              </StatNumber>
            </Stat>
            <Stat>
              <StatLabel>Total Samples</StatLabel>
              <StatNumber>
                {data.total_samples}
              </StatNumber>
            </Stat>
          </Grid>
        </Box>
      </VStack>
    );
  };

  return (
    <Container maxW="7xl" py={8}>
      <VStack spacing={8} align="stretch">
        {/* Header */}
        <Box textAlign="center">
          <Heading size="2xl" mb={4}>
            Real-Time Traffic Predictor
          </Heading>
          <Text fontSize="lg" color="gray.600" maxW="3xl" mx="auto">
            Advanced traffic prediction system that combines real-time data with historical patterns 
            to provide calibrated confidence scores for specific travel windows.
          </Text>
        </Box>

        {/* Prediction Form */}
        <Card>
          <CardHeader>
            <HStack spacing={3}>
              <Icon as={FiNavigation} color="blue.500" boxSize={6} />
              <Box>
                <Heading size="lg">Route Configuration</Heading>
                <Text color="gray.600">Configure your prediction parameters</Text>
              </Box>
            </HStack>
          </CardHeader>
          <CardBody>
            <Grid templateColumns={{ base: '1fr', lg: '1fr 1fr' }} gap={6}>
              <GridItem>
                <VStack spacing={6} align="stretch">
                  {/* Origin Selection */}
                  <FormControl isRequired>
                    <FormLabel>Origin Location</FormLabel>
                    <Select
                      placeholder="Select origin"
                      value={origin}
                      onChange={(e) => setOrigin(e.target.value)}
                      size="lg"
                    >
                      {locations.map((location) => (
                        <option key={location.name} value={location.name}>
                          {location.name}
                        </option>
                      ))}
                    </Select>
                  </FormControl>

                  {/* Destination Selection */}
                  <FormControl isRequired>
                    <FormLabel>Destination Location</FormLabel>
                    <Select
                      placeholder="Select destination"
                      value={destination}
                      onChange={(e) => setDestination(e.target.value)}
                      size="lg"
                    >
                      {locations.map((location) => (
                        <option key={location.name} value={location.name}>
                          {location.name}
                        </option>
                      ))}
                    </Select>
                  </FormControl>

                  {/* Route Preference */}
                  <FormControl>
                    <FormLabel>Route Preference</FormLabel>
                    <Select
                      value={routePreference}
                      onChange={(e) => setRoutePreference(e.target.value)}
                    >
                      <option value="fastest">Fastest Route</option>
                      <option value="shortest">Shortest Distance</option>
                      <option value="avoid_tolls">Avoid Tolls</option>
                      <option value="avoid_highways">Avoid Highways</option>
                    </Select>
                  </FormControl>
                </VStack>
              </GridItem>

              <GridItem>
                <VStack spacing={6} align="stretch">
                  {/* Prediction Time */}
                  <FormControl isRequired>
                    <FormLabel>Prediction Time</FormLabel>
                    <Input
                      type="datetime-local"
                      value={predictionTime}
                      onChange={(e) => setPredictionTime(e.target.value)}
                      size="lg"
                    />
                  </FormControl>

                  {/* Current Conditions Preview */}
                  <Box p={4} bg="blue.50" borderRadius="md">
                    <HStack spacing={3} mb={3}>
                      <Icon as={FiActivity} color="blue.500" />
                      <Heading size="md">Current Conditions</Heading>
                      <Button
                        size="sm"
                        variant="outline"
                        leftIcon={<FiRefreshCw />}
                        onClick={loadCurrentConditions}
                      >
                        Refresh
                      </Button>
                    </HStack>
                    {currentConditions ? (
                      <Text fontSize="sm" color="gray.600">
                        {currentConditions.total_routes} routes monitored
                        <br />
                        Last updated: {new Date(currentConditions.timestamp).toLocaleTimeString()}
                      </Text>
                    ) : (
                      <Text fontSize="sm" color="gray.500">
                        Click refresh to load current conditions
                      </Text>
                    )}
                  </Box>

                  {/* Generate Prediction Button */}
                  <Button
                    size="lg"
                    colorScheme="blue"
                    leftIcon={isPredicting ? <Spinner size="sm" /> : <FiTarget />}
                    onClick={generatePrediction}
                    isLoading={isPredicting}
                    loadingText="Generating Prediction..."
                    isDisabled={!origin || !destination || !predictionTime}
                  >
                    Generate Prediction
                  </Button>
                </VStack>
              </GridItem>
            </Grid>
          </CardBody>
        </Card>

        {/* Results Section */}
        {prediction && (
          <>
            {/* Prediction Results */}
            <Card>
              <CardHeader>
                <HStack spacing={3}>
                  <Icon as={FiTrendingUp} color="green.500" boxSize={6} />
                  <Heading size="lg">Traffic Prediction Results</Heading>
                  <Badge colorScheme="blue" size="lg">
                    {Math.round(prediction.confidence_score * 100)}% Confidence
                  </Badge>
                </HStack>
              </CardHeader>
              <CardBody>
                <Grid templateColumns={{ base: '1fr', md: 'repeat(3, 1fr)' }} gap={6}>
                  {/* Confidence Score */}
                  <ConfidenceScore score={prediction.confidence_score} />

                  {/* Predicted Duration */}
                  <Stat>
                    <StatLabel>Predicted Duration</StatLabel>
                    <StatNumber color="blue.500">
                      {Math.round(prediction.predicted_duration)} min
                    </StatNumber>
                    <StatHelpText>
                      <Badge colorScheme="blue">
                        {prediction.historical_analysis?.base_duration ? 
                          `${Math.round(prediction.historical_analysis.base_duration)} min historical avg` : 
                          'Historical data included'
                        }
                      </Badge>
                    </StatHelpText>
                  </Stat>

                  {/* Current Duration */}
                  <Stat>
                    <StatLabel>Current Duration</StatLabel>
                    <StatNumber color="orange.500">
                      {prediction.current_duration ? 
                        `${Math.round(prediction.current_duration)} min` : 
                        'N/A'
                      }
                    </StatNumber>
                    <StatHelpText>
                      Real-time data
                    </StatHelpText>
                  </Stat>
                </Grid>

                <Divider my={6} />

                {/* Traffic Conditions */}
                <Grid templateColumns={{ base: '1fr', md: 'repeat(2, 1fr)' }} gap={6}>
                  <Box>
                    <Heading size="md" mb={4}>Current Traffic Conditions</Heading>
                    <VStack align="stretch" spacing={3}>
                      <HStack justify="space-between">
                        <Text>Congestion Level:</Text>
                        <Badge colorScheme={getCongestionColor(prediction.traffic_conditions?.congestion_level)} size="lg">
                          {prediction.traffic_conditions?.congestion_level || 'Unknown'}
                        </Badge>
                      </HStack>
                      <HStack justify="space-between">
                        <Text>Average Speed:</Text>
                        <Text fontWeight="bold">
                          {Math.round(prediction.traffic_conditions?.average_speed || 0)} km/h
                        </Text>
                      </HStack>
                      <HStack justify="space-between">
                        <Text>Incidents:</Text>
                        <Badge colorScheme={prediction.traffic_conditions?.incidents > 0 ? 'red' : 'green'}>
                          {prediction.traffic_conditions?.incidents || 0}
                        </Badge>
                      </HStack>
                      <HStack justify="space-between">
                        <Text>Weather:</Text>
                        <HStack spacing={2}>
                          {getWeatherIcon(prediction.traffic_conditions?.weather)}
                          <Text textTransform="capitalize">
                            {prediction.traffic_conditions?.weather || 'Unknown'}
                          </Text>
                        </HStack>
                      </HStack>
                    </VStack>
                  </Box>

                  <Box>
                    <Heading size="md" mb={4}>Recommendations</Heading>
                    <VStack align="stretch" spacing={2}>
                      {prediction.recommendations?.map((rec, index) => (
                        <Alert key={index} status="info" variant="left-accent" size="sm">
                          <AlertIcon />
                          <AlertDescription fontSize="sm">
                            {rec}
                          </AlertDescription>
                        </Alert>
                      ))}
                    </VStack>
                  </Box>
                </Grid>

                <Divider my={6} />

                {/* Prediction Factors */}
                <Box>
                  <Heading size="md" mb={4}>Prediction Factors</Heading>
                  <Grid templateColumns={{ base: '1fr', md: 'repeat(3, 1fr)' }} gap={4}>
                    <Box p={3} bg="gray.50" borderRadius="md">
                      <Text fontSize="sm" fontWeight="bold" mb={1}>Real-time Multiplier</Text>
                      <Text fontSize="lg" color="blue.500">
                        {prediction.factors?.realtime_multiplier ? 
                          `${(prediction.factors.realtime_multiplier * 100).toFixed(0)}%` : 
                          'N/A'
                        }
                      </Text>
                    </Box>
                    <Box p={3} bg="gray.50" borderRadius="md">
                      <Text fontSize="sm" fontWeight="bold" mb={1}>Weather Impact</Text>
                      <Text fontSize="lg" color="orange.500">
                        {prediction.factors?.weather_multiplier ? 
                          `${(prediction.factors.weather_multiplier * 100).toFixed(0)}%` : 
                          'N/A'
                        }
                      </Text>
                    </Box>
                    <Box p={3} bg="gray.50" borderRadius="md">
                      <Text fontSize="sm" fontWeight="bold" mb={1}>Incident Impact</Text>
                      <Text fontSize="lg" color="red.500">
                        {prediction.factors?.incident_multiplier ? 
                          `${(prediction.factors.incident_multiplier * 100).toFixed(0)}%` : 
                          'N/A'
                        }
                      </Text>
                    </Box>
                  </Grid>
                </Box>
              </CardBody>
            </Card>

            {/* Detailed Analysis Tabs */}
            <Card>
              <CardBody>
                <Tabs index={activeTab} onChange={setActiveTab}>
                  <TabList>
                    <Tab>Historical Analysis</Tab>
                    <Tab>Current Conditions</Tab>
                    <Tab>Recent Predictions</Tab>
                  </TabList>

                  <TabPanels>
                    <TabPanel>
                      <HistoricalDataVisualization data={historicalData} />
                    </TabPanel>
                    
                    <TabPanel>
                      <TrafficConditionsTable conditions={currentConditions} />
                    </TabPanel>
                    
                    <TabPanel>
                      {recentPredictions.length > 0 ? (
                        <TableContainer>
                          <Table variant="simple">
                            <Thead>
                              <Tr>
                                <Th>Route</Th>
                                <Th>Prediction Time</Th>
                                <Th>Duration</Th>
                                <Th>Confidence</Th>
                                <Th>Actions</Th>
                              </Tr>
                            </Thead>
                            <Tbody>
                              {recentPredictions.map((pred) => (
                                <Tr key={pred.prediction_id}>
                                  <Td>
                                    <Text fontSize="sm" fontWeight="medium">
                                      {pred.origin} → {pred.destination}
                                    </Text>
                                  </Td>
                                  <Td>
                                    <Text fontSize="sm">
                                      {new Date(pred.prediction_time).toLocaleString()}
                                    </Text>
                                  </Td>
                                  <Td>
                                    <Text fontSize="sm">
                                      {Math.round(pred.predicted_duration)} min
                                    </Text>
                                  </Td>
                                  <Td>
                                    <Badge colorScheme={pred.confidence_score > 0.8 ? 'green' : 'yellow'} size="sm">
                                      {Math.round(pred.confidence_score * 100)}%
                                    </Badge>
                                  </Td>
                                  <Td>
                                    <Button
                                      size="sm"
                                      variant="outline"
                                      leftIcon={<FiEye />}
                                      onClick={() => {
                                        // Load and display detailed prediction
                                      }}
                                    >
                                      View Details
                                    </Button>
                                  </Td>
                                </Tr>
                              ))}
                            </Tbody>
                          </Table>
                        </TableContainer>
                      ) : (
                        <Text color="gray.500" textAlign="center">
                          No recent predictions available
                        </Text>
                      )}
                    </TabPanel>
                  </TabPanels>
                </Tabs>
              </CardBody>
            </Card>
          </>
        )}
      </VStack>
    </Container>
  );
};

export default RealTimeTrafficPredictor;