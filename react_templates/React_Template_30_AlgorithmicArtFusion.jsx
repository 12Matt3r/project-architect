/**
 * Template #30: Algorithmic Art Fusion - React Frontend
 * Advanced AI-powered artistic movement fusion using Directional-Stimulus Prompting interface
 * 
 * Author: MiniMax Agent
 * Date: 2025-11-17
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
  Slider,
  SliderTrack,
  SliderFilledTrack,
  SliderThumb,
  SliderMark,
  FormControl,
  FormLabel,
  Checkbox,
  CheckboxGroup,
  Stack,
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
  SimpleGrid,
  Skeleton,
  SkeletonText,
  useBreakpointValue
} from '@chakra-ui/react';
import {
  FaPalette,
  FaEye,
  FaDownload,
  FaShare,
  FaFilter,
  FaSearch,
  FaRobot,
  FaBrain,
  FaPaintBrush,
  FaHeart,
  FaLightbulb,
  FaExclamationTriangle,
  FaCheckCircle,
  FaTimesCircle,
  FaInfoCircle,
  FaBrush,
  FaMagic,
  FaSave,
  FaClipboard,
  FaExpand,
  FaCompress,
  FaHistory,
  FaStar,
  FaFire,
  FaLeaf,
  FaGem,
  FaWind,
  FaSun,
  FaMoon
} from 'react-icons/fa';

// Color mode values
const bgColor = useColorModeValue('gray.50', 'gray.900');
const cardBg = useColorModeValue('white', 'gray.800');
const borderColor = useColorModeValue('gray.200', 'gray.600');
const highlightColor = useColorModeValue('purple.50', 'purple.900');

// Types
interface Movement {
  name: string;
  period: string;
  key_artists: string[];
  primary_emotions: string[];
  color_characteristics: number;
  description: string;
}

interface FusionElement {
  visual_synthesis: {
    composition: string;
    lighting: string;
    texture: string;
  };
  color_harmonization: {
    primary_palette: string[];
    accent_palette: string[];
    fusion_strategy: string;
  };
  composition_fusion: {
    fusion_style: string;
    dominant_approach: string;
  };
  emotional_synthesis: {
    synthesized_emotions: string[];
    emotional_balance: string;
    target_alignment: string;
  };
  technical_fusion: {
    technique_fusion: string;
    material_harmonization: string;
    stylistic_synthesis: string;
  };
}

interface FusionResult {
  project_id: string;
  generated_prompt: string;
  artistic_elements: FusionElement;
  fusion_analysis: {
    coherence_score: number;
    innovation_level: string;
    aesthetic_balance: string;
  };
  movement_analysis: {
    movement_1: any;
    movement_2: any;
  };
  visual_principles: any;
  emotional_synthesis: string[];
  technical_specifications: any;
  timestamp: string;
}

// Mock data for demonstration
const mockMovements: Movement[] = [
  {
    name: "Baroque",
    period: "1600-1750",
    key_artists: ["Caravaggio", "Rembrandt", "Rubens"],
    primary_emotions: ["Dramatic", "Passionate", "Religious fervor"],
    color_characteristics: 6,
    description: "Baroque art movement from 1600-1750"
  },
  {
    name: "Minimalism",
    period: "1960s-1970s",
    key_artists: ["Donald Judd", "Agnes Martin", "Frank Stella"],
    primary_emotions: ["Serene", "Contemplative", "Peaceful"],
    color_characteristics: 6,
    description: "Minimalism art movement from 1960s-1970s"
  },
  {
    name: "Impressionism",
    period: "1860s-1880s",
    key_artists: ["Monet", "Renoir", "Degas"],
    primary_emotions: ["Joyful", "Peaceful", "Optimistic"],
    color_characteristics: 6,
    description: "Impressionism art movement from 1860s-1880s"
  }
];

const App: React.FC = () => {
  const [selectedMovement1, setSelectedMovement1] = useState<string>('');
  const [selectedMovement2, setSelectedMovement2] = useState<string>('');
  const [fusionIntensity, setFusionIntensity] = useState<number>(50);
  const [targetEmotion, setTargetEmotion] = useState<string>('balanced');
  const [stylePreferences, setStylePreferences] = useState<string[]>([]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [fusionResult, setFusionResult] = useState<FusionResult | null>(null);
  const [availableMovements, setAvailableMovements] = useState<Movement[]>(mockMovements);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterPeriod, setFilterPeriod] = useState<string>('all');
  const [showPreview, setShowPreview] = useState(false);
  const { isOpen, onOpen, onClose } = useDisclosure();
  const toast = useToast();
  const isMobile = useBreakpointValue({ base: true, md: false });

  // Load available movements on component mount
  useEffect(() => {
    // In a real app, this would fetch from the API
    setAvailableMovements(mockMovements);
  }, []);

  // Event handlers
  const handleMovementSelect = useCallback((movement: string, position: 'first' | 'second') => {
    if (position === 'first') {
      setSelectedMovement1(movement);
      if (movement === selectedMovement2) {
        setSelectedMovement2('');
      }
    } else {
      setSelectedMovement2(movement);
      if (movement === selectedMovement1) {
        setSelectedMovement1('');
      }
    }
  }, [selectedMovement1, selectedMovement2]);

  const handleGenerateFusion = useCallback(async () => {
    if (!selectedMovement1 || !selectedMovement2) {
      toast({
        title: 'Select Both Movements',
        description: 'Please select two artistic movements to create a fusion',
        status: 'warning',
        duration: 5000,
        isClosable: true,
      });
      return;
    }

    setIsGenerating(true);

    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 3000));

      const mockResult: FusionResult = {
        project_id: `fusion_${Date.now()}`,
        generated_prompt: `Create an artwork that synthesizes ${selectedMovement1} and ${selectedMovement2} artistic movements:\n\n**VISUAL COMPOSITION**: Fusion of ${selectedMovement1} composition principles with ${selectedMovement2} structural elements\n**LIGHTING APPROACH**: Dramatic lighting balanced with even illumination\n**TEXTURAL TREATMENT**: Smooth surfaces with textured accent areas\n**COLOR PALETTE**: Warm golden tones with cool accent colors\n**COMPOSITIONAL STYLE**: Dynamic movement balanced with static stability\n**EMOTIONAL ATMOSPHERE**: Evoke dramatic, passionate, serene emotions\n**TECHNICAL APPROACH**: Use techniques that honor both movements while creating something new and innovative\n\n**FUSION BALANCE**: ${fusionIntensity / 100} (0.0 = pure first movement, 1.0 = pure second movement)\n**ARTISTIC VISION**: Create a piece that feels both familiar and revolutionary, drawing from the strengths of both movements while establishing its own unique identity.`,
        artistic_elements: {
          visual_synthesis: {
            composition: `Fusion of ${selectedMovement1} composition principles with ${selectedMovement2} structural elements`,
            lighting: "Dramatic lighting balanced with even illumination",
            texture: "Smooth surfaces with textured accent areas"
          },
          color_harmonization: {
            primary_palette: ["#8B4513", "#DAA520", "#F5DEB3"],
            accent_palette: ["#2F4F4F", "#4682B4", "#98FB98"],
            fusion_strategy: "Balanced fusion with equal weight to both movements"
          },
          composition_fusion: {
            fusion_style: "Dynamic movement balanced with static stability",
            dominant_approach: "balanced"
          },
          emotional_synthesis: {
            synthesized_emotions: ["Dramatic", "Passionate", "Serene", "Contemplative"],
            emotional_balance: "Strong emotional compatibility with complementary differences",
            target_alignment: targetEmotion
          },
          technical_fusion: {
            technique_fusion: "Integrated techniques: traditional painting, geometric construction, surface texture",
            material_harmonization: "Harmonized materials: traditional art materials, oil paint, canvas, metal, glass",
            stylistic_synthesis: "Unified stylistic approach that respects both traditions while innovating"
          }
        },
        fusion_analysis: {
          coherence_score: 0.85,
          innovation_level: "High",
          aesthetic_balance: "Well-balanced fusion with clear artistic vision"
        },
        movement_analysis: {
          movement_1: { name: selectedMovement1, characteristics: ["dramatic", "rich colors"] },
          movement_2: { name: selectedMovement2, characteristics: ["minimal", "clean lines"] }
        },
        visual_principles: {},
        emotional_synthesis: ["Dramatic", "Passionate", "Serene", "Contemplative"],
        technical_specifications: {
          recommended_medium: "Digital painting or mixed media",
          canvas_size: "Medium to large format for full impact",
          color_temperature: "Warm with cool accents",
          value_structure: "Full value range with emphasis on contrast"
        },
        timestamp: new Date().toISOString()
      };

      setFusionResult(mockResult);
      setShowPreview(true);

      toast({
        title: 'Fusion Generated!',
        description: 'Artistic fusion prompt has been created successfully',
        status: 'success',
        duration: 5000,
        isClosable: true,
      });

    } catch (error) {
      toast({
        title: 'Generation Failed',
        description: 'Failed to generate artistic fusion. Please try again.',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setIsGenerating(false);
    }
  }, [selectedMovement1, selectedMovement2, fusionIntensity, targetEmotion, toast]);

  const downloadPrompt = () => {
    if (!fusionResult) return;
    
    const content = `ARTISTIC FUSION PROJECT
Movement 1: ${selectedMovement1}
Movement 2: ${selectedMovement2}
Fusion Intensity: ${fusionIntensity}%
Target Emotion: ${targetEmotion}

${fusionResult.generated_prompt}

Generated: ${new Date(fusionResult.timestamp).toLocaleString()}
Project ID: ${fusionResult.project_id}
`;
    
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `artistic-fusion-${selectedMovement1}-${selectedMovement2}.txt`;
    a.click();
    URL.revokeObjectURL(url);

    toast({
      title: 'Download Started',
      description: 'Fusion prompt is being downloaded',
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

  const getEmotionIcon = (emotion: string) => {
    const iconMap: { [key: string]: any } = {
      'dramatic': FaFire,
      'passionate': FaHeart,
      'serene': FaLeaf,
      'contemplative': FaMoon,
      'peaceful': FaLeaf,
      'joyful': FaSun,
      'dramatic': FaFire,
      'mysterious': FaGem,
      'intense': FaFire,
      'calm': FaWind
    };
    return iconMap[emotion.toLowerCase()] || FaStar;
  };

  const filteredMovements = availableMovements.filter(movement => {
    const matchesSearch = searchTerm === '' || 
      movement.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      movement.key_artists.some(artist => artist.toLowerCase().includes(searchTerm.toLowerCase()));
    
    const matchesFilter = filterPeriod === 'all' || movement.period.includes(filterPeriod);
    
    return matchesSearch && matchesFilter;
  });

  return (
    <Box bg={bgColor} minH="100vh">
      <Container maxW="7xl" py={8}>
        {/* Header */}
        <VStack spacing={6} align="stretch">
          <Box textAlign="center">
            <HStack justify="center" spacing={4} mb={4}>
              <Icon as={FaPalette} boxSize={8} color="purple.500" />
              <Heading size="2xl" bgGradient="linear(to-r, purple.400, pink.500)" bgClip="text">
                Algorithmic Art Fusion
              </Heading>
              <Icon as={FaBrain} boxSize={8} color="pink.500" />
            </HStack>
            <Text fontSize="xl" color="gray.600">
              AI-powered artistic movement fusion using Directional-Stimulus Prompting
            </Text>
          </Box>

          {/* Movement Selection */}
          <Card bg={cardBg} borderWidth="1px" borderColor={borderColor}>
            <CardHeader>
              <HStack>
                <Icon as={FaBrush} color="purple.500" />
                <Heading size="md">Select Artistic Movements</Heading>
              </HStack>
            </CardHeader>
            <CardBody>
              <Grid templateColumns={isMobile ? "1fr" : "repeat(2, 1fr)"} gap={6}>
                {/* Movement 1 Selection */}
                <Box>
                  <Text fontWeight="medium" mb={3}>First Movement</Text>
                  <Select
                    placeholder="Select first movement..."
                    value={selectedMovement1}
                    onChange={(e) => handleMovementSelect(e.target.value, 'first')}
                    bg={selectedMovement1 ? 'purple.50' : undefined}
                  >
                    {availableMovements.map((movement) => (
                      <option key={movement.name} value={movement.name}>
                        {movement.name} ({movement.period})
                      </option>
                    ))}
                  </Select>
                  
                  {selectedMovement1 && (
                    <Box mt={3} p={3} bg="purple.50" borderRadius="md">
                      <Text fontSize="sm" fontWeight="medium" mb={2}>Selected: {selectedMovement1}</Text>
                      <Wrap>
                        {mockMovements.find(m => m.name === selectedMovement1)?.primary_emotions.map((emotion, index) => {
                          const EmotionIcon = getEmotionIcon(emotion);
                          return (
                            <WrapItem key={index}>
                              <Tag size="sm" colorScheme="purple" variant="subtle">
                                <TagLeftIcon as={EmotionIcon} />
                                <TagLabel>{emotion}</TagLabel>
                              </Tag>
                            </WrapItem>
                          );
                        })}
                      </Wrap>
                    </Box>
                  )}
                </Box>

                {/* Movement 2 Selection */}
                <Box>
                  <Text fontWeight="medium" mb={3}>Second Movement</Text>
                  <Select
                    placeholder="Select second movement..."
                    value={selectedMovement2}
                    onChange={(e) => handleMovementSelect(e.target.value, 'second')}
                    bg={selectedMovement2 ? 'pink.50' : undefined}
                  >
                    {availableMovements.filter(m => m.name !== selectedMovement1).map((movement) => (
                      <option key={movement.name} value={movement.name}>
                        {movement.name} ({movement.period})
                      </option>
                    ))}
                  </Select>
                  
                  {selectedMovement2 && (
                    <Box mt={3} p={3} bg="pink.50" borderRadius="md">
                      <Text fontSize="sm" fontWeight="medium" mb={2}>Selected: {selectedMovement2}</Text>
                      <Wrap>
                        {mockMovements.find(m => m.name === selectedMovement2)?.primary_emotions.map((emotion, index) => {
                          const EmotionIcon = getEmotionIcon(emotion);
                          return (
                            <WrapItem key={index}>
                              <Tag size="sm" colorScheme="pink" variant="subtle">
                                <TagLeftIcon as={EmotionIcon} />
                                <TagLabel>{emotion}</TagLabel>
                              </Tag>
                            </WrapItem>
                          );
                        })}
                      </Wrap>
                    </Box>
                  )}
                </Box>
              </Grid>

              {/* Search and Filter */}
              <Grid templateColumns={isMobile ? "1fr" : "repeat(2, 1fr)"} gap={4} mt={6}>
                <Box>
                  <Text fontSize="sm" fontWeight="medium" mb={1}>Search Movements:</Text>
                  <Input
                    placeholder="Search by name or artist..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    leftElement={<Icon as={FaSearch} color="gray.400" />}
                    size="sm"
                  />
                </Box>
                <Box>
                  <Text fontSize="sm" fontWeight="medium" mb={1}>Filter by Period:</Text>
                  <Select
                    value={filterPeriod}
                    onChange={(e) => setFilterPeriod(e.target.value)}
                    size="sm"
                  >
                    <option value="all">All Periods</option>
                    <option value="1600">17th Century</option>
                    <option value="1800">19th Century</option>
                    <option value="1900">20th Century</option>
                  </Select>
                </Box>
              </Grid>
            </CardBody>
          </Card>

          {/* Fusion Parameters */}
          <Card bg={cardBg} borderWidth="1px" borderColor={borderColor}>
            <CardHeader>
              <HStack>
                <Icon as={FaCog} color="blue.500" />
                <Heading size="md">Fusion Parameters</Heading>
              </HStack>
            </CardHeader>
            <CardBody>
              <VStack spacing={6} align="stretch">
                {/* Fusion Intensity */}
                <Box>
                  <FormControl>
                    <FormLabel>
                      <HStack>
                        <Text fontWeight="medium">Fusion Intensity</Text>
                        <Badge colorScheme="blue">{fusionIntensity}%</Badge>
                      </HStack>
                    </FormLabel>
                    <Slider
                      value={fusionIntensity}
                      onChange={setFusionIntensity}
                      min={0}
                      max={100}
                      step={5}
                    >
                      <SliderMark value={0} mt={2} ml={-4} fontSize="sm">
                        Pure Movement 1
                      </SliderMark>
                      <SliderMark value={50} mt={2} ml={-8} fontSize="sm">
                        Balanced
                      </SliderMark>
                      <SliderMark value={100} mt={2} ml={-4} fontSize="sm">
                        Pure Movement 2
                      </SliderMark>
                      <SliderTrack>
                        <SliderFilledTrack />
                      </SliderTrack>
                      <SliderThumb />
                    </Slider>
                  </FormControl>
                </Box>

                {/* Target Emotion */}
                <Box>
                  <Text fontWeight="medium" mb={3}>Target Emotional Quality</Text>
                  <SimpleGrid columns={isMobile ? 2 : 4} spacing={3}>
                    {['balanced', 'harmonious', 'dramatic', 'serene'].map((emotion) => (
                      <Button
                        key={emotion}
                        size="sm"
                        variant={targetEmotion === emotion ? 'solid' : 'outline'}
                        colorScheme={targetEmotion === emotion ? 'purple' : 'gray'}
                        onClick={() => setTargetEmotion(emotion)}
                        leftIcon={<Icon as={getEmotionIcon(emotion)} />}
                      >
                        {emotion.charAt(0).toUpperCase() + emotion.slice(1)}
                      </Button>
                    ))}
                  </SimpleGrid>
                </Box>

                {/* Style Preferences */}
                <Box>
                  <Text fontWeight="medium" mb={3}>Style Preferences (Optional)</Text>
                  <CheckboxGroup value={stylePreferences} onChange={setStylePreferences}>
                    <Stack direction={isMobile ? 'column' : 'row'} spacing={4}>
                      <Checkbox value="geometric">Geometric Forms</Checkbox>
                      <Checkbox value="organic">Organic Shapes</Checkbox>
                      <Checkbox value="bold_colors">Bold Colors</Checkbox>
                      <Checkbox value="subtle_tones">Subtle Tones</Checkbox>
                      <Checkbox value="high_detail">High Detail</Checkbox>
                      <Checkbox value="minimal_detail">Minimal Detail</Checkbox>
                    </Stack>
                  </CheckboxGroup>
                </Box>

                {/* Generate Button */}
                <Button
                  colorScheme="purple"
                  size="lg"
                  leftIcon={isGenerating ? <Spinner size="sm" /> : <FaMagic />}
                  onClick={handleGenerateFusion}
                  isLoading={isGenerating}
                  loadingText="Generating Fusion..."
                  isDisabled={!selectedMovement1 || !selectedMovement2}
                >
                  Generate Artistic Fusion
                </Button>
              </VStack>
            </CardBody>
          </Card>

          {/* Results Section */}
          {fusionResult && (
            <VStack spacing={6} align="stretch">
              {/* Fusion Overview */}
              <Card bg={cardBg} borderWidth="1px" borderColor={borderColor}>
                <CardHeader>
                  <HStack justify="space-between">
                    <HStack>
                      <Icon as={FaEye} color="green.500" />
                      <Heading size="md">Fusion Result</Heading>
                    </HStack>
                    <HStack>
                      <Button
                        leftIcon={<FaDownload />}
                        colorScheme="green"
                        variant="outline"
                        size="sm"
                        onClick={downloadPrompt}
                      >
                        Download Prompt
                      </Button>
                      <Button
                        leftIcon={<FaClipboard />}
                        size="sm"
                        variant="outline"
                        onClick={() => copyToClipboard(fusionResult.generated_prompt)}
                      >
                        Copy Prompt
                      </Button>
                    </HStack>
                  </HStack>
                </CardHeader>
                <CardBody>
                  <Grid templateColumns="repeat(auto-fit, minmax(200px, 1fr))" gap={6}>
                    <Stat>
                      <StatLabel>Fusion Quality</StatLabel>
                      <StatNumber color="green.500">{(fusionResult.fusion_analysis.coherence_score * 100).toFixed(0)}%</StatNumber>
                      <StatHelpText>
                        <StatArrow type="increase" />
                        Coherence score
                      </StatHelpText>
                    </Stat>
                    <Stat>
                      <StatLabel>Innovation Level</StatLabel>
                      <StatNumber>{fusionResult.fusion_analysis.innovation_level}</StatNumber>
                      <StatHelpText>
                        <Icon as={FaLightbulb} mr={1} />
                        Creative potential
                      </StatHelpText>
                    </Stat>
                    <Stat>
                      <StatLabel>Fusion Balance</StatLabel>
                      <StatNumber>{fusionIntensity}%</StatNumber>
                      <StatHelpText>
                        <Icon as={FaStar} mr={1} />
                        {selectedMovement1} → {selectedMovement2}
                      </StatHelpText>
                    </Stat>
                    <Stat>
                      <StatLabel>Project ID</StatLabel>
                      <StatNumber fontSize="md" fontFamily="mono">
                        {fusionResult.project_id.slice(0, 8)}...
                      </StatNumber>
                      <StatHelpText>
                        <Icon as={FaHistory} mr={1} />
                        {new Date(fusionResult.timestamp).toLocaleString()}
                      </StatHelpText>
                    </Stat>
                  </Grid>
                </CardBody>
              </Card>

              {/* Detailed Analysis Tabs */}
              <Card bg={cardBg} borderWidth="1px" borderColor={borderColor}>
                <CardBody>
                  <Tabs variant="enclosed">
                    <TabList>
                      <Tab><Icon as={FaPalette} mr={2} />Generated Prompt</Tab>
                      <Tab><Icon as={FaBrush} mr={2} />Visual Elements</Tab>
                      <Tab><Icon as={FaHeart} mr={2} />Emotional Synthesis</Tab>
                      <Tab><Icon as={FaCog} mr={2} />Technical Specs</Tab>
                    </TabList>

                    <TabPanels>
                      {/* Generated Prompt Tab */}
                      <TabPanel>
                        <VStack align="stretch" spacing={4}>
                          <HStack justify="space-between">
                            <Heading size="sm">Directional-Stimulus Prompt</Heading>
                            <HStack>
                              <Button
                                size="sm"
                                leftIcon={<FaClipboard />}
                                onClick={() => copyToClipboard(fusionResult.generated_prompt)}
                              >
                                Copy
                              </Button>
                              <Button
                                size="sm"
                                colorScheme="purple"
                                leftIcon={<FaDownload />}
                                onClick={downloadPrompt}
                              >
                                Download
                              </Button>
                            </HStack>
                          </HStack>
                          
                          <Box
                            bg="gray.50"
                            borderWidth="1px"
                            borderColor={borderColor}
                            borderRadius="md"
                            p={4}
                            maxH="400px"
                            overflowY="auto"
                            fontFamily="mono"
                            fontSize="sm"
                            whiteSpace="pre-wrap"
                          >
                            {fusionResult.generated_prompt}
                          </Box>
                        </VStack>
                      </TabPanel>

                      {/* Visual Elements Tab */}
                      <TabPanel>
                        <VStack align="stretch" spacing={6}>
                          {/* Color Palette */}
                          <Box>
                            <Text fontWeight="medium" mb={3}>Color Harmonization</Text>
                            <Grid templateColumns="repeat(auto-fit, minmax(100px, 1fr))" gap={2}>
                              {fusionResult.artistic_elements.color_harmonization.primary_palette.map((color, index) => (
                                <Box key={index}>
                                  <Box
                                    w="100%"
                                    h="60px"
                                    bg={color}
                                    borderRadius="md"
                                    borderWidth="1px"
                                    borderColor={borderColor}
                                    mb={1}
                                  />
                                  <Text fontSize="xs" textAlign="center" fontFamily="mono">
                                    {color}
                                  </Text>
                                </Box>
                              ))}
                            </Grid>
                            <Text fontSize="sm" color="gray.600" mt={2}>
                              {fusionResult.artistic_elements.color_harmonization.fusion_strategy}
                            </Text>
                          </Box>

                          {/* Visual Synthesis */}
                          <Box>
                            <Text fontWeight="medium" mb={3}>Visual Synthesis</Text>
                            <Grid templateColumns="repeat(auto-fit, minmax(250px, 1fr))" gap={4}>
                              <Box p={3} bg={highlightColor} borderRadius="md">
                                <Text fontWeight="medium" mb={1}>Composition</Text>
                                <Text fontSize="sm">{fusionResult.artistic_elements.visual_synthesis.composition}</Text>
                              </Box>
                              <Box p={3} bg={highlightColor} borderRadius="md">
                                <Text fontWeight="medium" mb={1}>Lighting</Text>
                                <Text fontSize="sm">{fusionResult.artistic_elements.visual_synthesis.lighting}</Text>
                              </Box>
                              <Box p={3} bg={highlightColor} borderRadius="md">
                                <Text fontWeight="medium" mb={1}>Texture</Text>
                                <Text fontSize="sm">{fusionResult.artistic_elements.visual_synthesis.texture}</Text>
                              </Box>
                            </Grid>
                          </Box>

                          {/* Composition Style */}
                          <Box>
                            <Text fontWeight="medium" mb={3}>Composition Fusion</Text>
                            <Text fontSize="sm">{fusionResult.artistic_elements.composition_fusion.fusion_style}</Text>
                            <Badge colorScheme="purple" mt={2}>
                              Dominant: {fusionResult.artistic_elements.composition_fusion.dominant_approach}
                            </Badge>
                          </Box>
                        </VStack>
                      </TabPanel>

                      {/* Emotional Synthesis Tab */}
                      <TabPanel>
                        <VStack align="stretch" spacing={6}>
                          {/* Synthesized Emotions */}
                          <Box>
                            <Text fontWeight="medium" mb={3}>Synthesized Emotions</Text>
                            <Wrap>
                              {fusionResult.emotional_synthesis.map((emotion, index) => {
                                const EmotionIcon = getEmotionIcon(emotion);
                                return (
                                  <WrapItem key={index}>
                                    <Tag size="lg" colorScheme="purple" variant="solid">
                                      <TagLeftIcon as={EmotionIcon} />
                                      <TagLabel>{emotion}</TagLabel>
                                    </Tag>
                                  </WrapItem>
                                );
                              })}
                            </Wrap>
                          </Box>

                          {/* Emotional Analysis */}
                          <Box>
                            <Text fontWeight="medium" mb={3}>Emotional Analysis</Text>
                            <Grid templateColumns="repeat(auto-fit, minmax(200px, 1fr))" gap={4}>
                              <Box p={3} bg={highlightColor} borderRadius="md">
                                <Text fontWeight="medium" mb={1}>Balance</Text>
                                <Text fontSize="sm">{fusionResult.artistic_elements.emotional_synthesis.emotional_balance}</Text>
                              </Box>
                              <Box p={3} bg={highlightColor} borderRadius="md">
                                <Text fontWeight="medium" mb={1}>Target Alignment</Text>
                                <Text fontSize="sm">{fusionResult.artistic_elements.emotional_synthesis.target_alignment}</Text>
                              </Box>
                            </Grid>
                          </Box>

                          {/* Movement Comparison */}
                          <Box>
                            <Text fontWeight="medium" mb={3}>Movement Emotional Profiles</Text>
                            <TableContainer>
                              <Table size="sm" variant="simple">
                                <Thead>
                                  <Tr>
                                    <Th>Movement</Th>
                                    <Th>Primary Emotions</Th>
                                  </Tr>
                                </Thead>
                                <Tbody>
                                  <Tr>
                                    <Td fontWeight="medium">{selectedMovement1}</Td>
                                    <Td>
                                      <Wrap>
                                        {mockMovements.find(m => m.name === selectedMovement1)?.primary_emotions.map((emotion, index) => (
                                          <WrapItem key={index}>
                                            <Tag size="sm" colorScheme="purple" variant="subtle">
                                              <TagLabel>{emotion}</TagLabel>
                                            </Tag>
                                          </WrapItem>
                                        ))}
                                      </Wrap>
                                    </Td>
                                  </Tr>
                                  <Tr>
                                    <Td fontWeight="medium">{selectedMovement2}</Td>
                                    <Td>
                                      <Wrap>
                                        {mockMovements.find(m => m.name === selectedMovement2)?.primary_emotions.map((emotion, index) => (
                                          <WrapItem key={index}>
                                            <Tag size="sm" colorScheme="pink" variant="subtle">
                                              <TagLabel>{emotion}</TagLabel>
                                            </Tag>
                                          </WrapItem>
                                        ))}
                                      </Wrap>
                                    </Td>
                                  </Tr>
                                </Tbody>
                              </Table>
                            </TableContainer>
                          </Box>
                        </VStack>
                      </TabPanel>

                      {/* Technical Specifications Tab */}
                      <TabPanel>
                        <VStack align="stretch" spacing={4}>
                          {Object.entries(fusionResult.technical_specifications).map(([key, value]) => (
                            <Box key={key} p={3} bg={highlightColor} borderRadius="md">
                              <Text fontWeight="medium" mb={1}>
                                {key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                              </Text>
                              <Text fontSize="sm">{value}</Text>
                            </Box>
                          ))}
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
